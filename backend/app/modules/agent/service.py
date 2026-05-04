import re
from typing import Dict, Any, List, Optional

from openai import (
    RateLimitError,
    AuthenticationError,
    PermissionDeniedError,
    BadRequestError,
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
)
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.config import settings
from app.modules.agent.tools import (
    create_cal_booking,
    list_cal_bookings_by_email,
)
from app.modules.agent.schemas import UserIntentExtraction
from app.modules.agent.prompts import AGENT_EXTRACTION_PROMPT


class AgentService:
    def __init__(self):
        self.model = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0,
            timeout=30,
            max_retries=2,
        )

        self.extractor = self.model.with_structured_output(
            UserIntentExtraction,
            method="function_calling",
            include_raw=False,
        )

        self.tools = [
            create_cal_booking,
            list_cal_bookings_by_email,
        ]

        self.tool_map = {
            "create_cal_booking": create_cal_booking,
            "list_cal_bookings_by_email": list_cal_bookings_by_email,
        }

        # Demo memory. Production should use Redis or database.
        self.pending_bookings: Dict[str, Dict[str, Any]] = {}
        self.pending_lists: Dict[str, Dict[str, Any]] = {}

    def chat(self, user_message: str, session_id: str = "default") -> str:
        try:
            extraction = self._extract_user_intent(user_message)

            if extraction.action == "cancel_pending":
                self.pending_bookings.pop(session_id, None)
                self.pending_lists.pop(session_id, None)
                return "Okay, I cancelled the current unfinished flow."

            # 1. If user is already in booking flow, keep collecting booking info.
            # Only switch to list flow if the user explicitly asks to list/show/check meetings.
            if session_id in self.pending_bookings:
                if self._is_explicit_list_request(user_message):
                    self.pending_bookings.pop(session_id, None)
                    return self._handle_list_bookings_flow(
                        session_id=session_id,
                        extraction=extraction,
                        raw_message=user_message,
                    )

                return self._handle_create_booking_flow(
                    session_id=session_id,
                    extraction=extraction,
                    raw_message=user_message,
                )

            # 2. If user is already in list flow, keep collecting email.
            # Only switch to booking flow if the user explicitly starts a booking request.
            if session_id in self.pending_lists:
                if extraction.action == "create_booking":
                    self.pending_lists.pop(session_id, None)
                    return self._handle_create_booking_flow(
                        session_id=session_id,
                        extraction=extraction,
                        raw_message=user_message,
                    )

                return self._handle_list_bookings_flow(
                    session_id=session_id,
                    extraction=extraction,
                    raw_message=user_message,
                )

            # 3. No pending flow yet. Start based on extracted intent.
            if extraction.action == "create_booking":
                return self._handle_create_booking_flow(
                    session_id=session_id,
                    extraction=extraction,
                    raw_message=user_message,
                )

            if extraction.action == "list_bookings":
                return self._handle_list_bookings_flow(
                    session_id=session_id,
                    extraction=extraction,
                    raw_message=user_message,
                )

            return (
                "I can help you book a meeting or list scheduled meetings. "
                "For example: 'Book a meeting tomorrow at 3pm' or "
                "'Show meetings for testuser@example.com'."
            )

        except AuthenticationError:
            return "OpenAI API key is invalid or missing. Please check your OPENAI_API_KEY in the .env file."

        except PermissionDeniedError:
            return "OpenAI API permission denied. Please check whether your API key has access to this model."

        except RateLimitError as e:
            error_message = str(e)

            if "insufficient_quota" in error_message:
                return "OpenAI API quota is insufficient. Please check your billing, credits, or usage limit."

            return "OpenAI API rate limit reached. Please try again later."

        except BadRequestError as e:
            return f"OpenAI request error. Please check the model name or request format. Details: {str(e)}"

        except (APIConnectionError, APITimeoutError):
            return "OpenAI API connection failed or timed out. Please try again."

        except InternalServerError:
            return "OpenAI server error. Please try again later."

        except Exception as e:
            return f"Unexpected agent error: {str(e)}"

    def _extract_user_intent(self, user_message: str) -> UserIntentExtraction:
        messages = [
            SystemMessage(content=AGENT_EXTRACTION_PROMPT),
            HumanMessage(content=user_message),
        ]

        return self.extractor.invoke(messages)

    def _handle_create_booking_flow(
        self,
        session_id: str,
        extraction: UserIntentExtraction,
        raw_message: str = "",
    ) -> str:
        current_state = self.pending_bookings.get(session_id, {})

        extracted_data = {
            "name": extraction.name,
            "email": extraction.email or self._extract_email_fallback(raw_message),
            "date": extraction.date or self._extract_date_fallback(raw_message),
            "time": extraction.time or self._extract_time_fallback(raw_message),
            "timezone": extraction.timezone,
            "reason": extraction.reason,
        }

        for key, value in extracted_data.items():
            if value:
                current_state[key] = value

        if not current_state.get("timezone"):
            current_state["timezone"] = settings.CAL_TIMEZONE

        self.pending_bookings[session_id] = current_state

        missing_fields = self._get_missing_booking_fields(current_state)

        if missing_fields:
            return self._ask_for_missing_booking_fields(current_state, missing_fields)
        
        print("CURRENT BOOKING STATE:", current_state)
        
        result = self._run_tool(
            tool_name="create_cal_booking",
            tool_args={
                "name": current_state["name"],
                "email": current_state["email"],
                "date": current_state["date"],
                "time": current_state["time"],
                "reason": current_state["reason"],
                "timezone": current_state["timezone"],
            },
        )
        
        # Only clear pending booking if booking succeeds.
        if "Booking created successfully" in result:
            self.pending_bookings.pop(session_id, None)
            return result

        # If booking fails, keep the existing information.
        # User can provide a new date or time without re-entering everything.
        self.pending_bookings[session_id] = current_state

        return (
            f"{result}\n\n"
            "The booking was not completed. I kept your previous information, "
            "so you can just provide a new date or time."
        )

    def _handle_list_bookings_flow(
        self,
        session_id: str,
        extraction: UserIntentExtraction,
        raw_message: str = "",
    ) -> str:
        current_state = self.pending_lists.get(session_id, {})

        email = extraction.email or self._extract_email_fallback(raw_message)

        if email:
            current_state["email"] = email

        self.pending_lists[session_id] = current_state

        if not current_state.get("email"):
            return "Sure. What email should I use to look up the scheduled meetings?"

        result = self._run_tool(
            tool_name="list_cal_bookings_by_email",
            tool_args={
                "email": current_state["email"],
            },
        )

        # If bookings are found, finish the list flow.
        if "Found" in result and "booking(s)" in result:
            self.pending_lists.pop(session_id, None)
            return result

        # If no bookings found or lookup failed, keep the list flow.
        # This lets user provide another email without restarting.
        self.pending_lists[session_id] = current_state

        return (
            f"{result}\n\n"
            "You can provide another email address if you want me to check a different account."
        )

    def _get_missing_booking_fields(self, state: Dict[str, Any]) -> List[str]:
        required_fields = ["name", "email", "date", "time", "reason"]

        return [
            field
            for field in required_fields
            if not state.get(field)
        ]

    def _ask_for_missing_booking_fields(
        self,
        state: Dict[str, Any],
        missing_fields: List[str],
    ) -> str:
        known_parts = []

        if state.get("name"):
            known_parts.append(f"name: {state['name']}")
        if state.get("email"):
            known_parts.append(f"email: {state['email']}")
        if state.get("date"):
            known_parts.append(f"date: {state['date']}")
        if state.get("time"):
            known_parts.append(f"time: {state['time']}")
        if state.get("reason"):
            known_parts.append(f"reason: {state['reason']}")
        if state.get("timezone"):
            known_parts.append(f"timezone: {state['timezone']}")

        known_text = ""
        if known_parts:
            known_text = "I have: " + ", ".join(known_parts) + ". "

        readable_missing = ", ".join(missing_fields)

        return (
            f"{known_text}"
            f"I still need the following information to book the meeting: {readable_missing}."
        )

    def _run_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        selected_tool = self.tool_map.get(tool_name)

        if selected_tool is None:
            return f"Tool '{tool_name}' is not supported."

        tool_call = {
            "name": tool_name,
            "args": tool_args,
            "id": f"manual_{tool_name}",
            "type": "tool_call",
        }

        tool_result = selected_tool.invoke(tool_call)

        if hasattr(tool_result, "content"):
            return str(tool_result.content)

        return str(tool_result)

    def _extract_email_fallback(self, text: str) -> Optional[str]:
        match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        return match.group(0) if match else None
    
    def _extract_date_fallback(self, text: str) -> Optional[str]:
        match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", text)
        return match.group(0) if match else None


    def _extract_time_fallback(self, text: str) -> Optional[str]:
        text_lower = text.lower()

        # Match 1pm, 1 pm, 1:30pm, 1:30 pm
        match = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", text_lower)

        if match:
            hour = int(match.group(1))
            minute = int(match.group(2) or 0)
            period = match.group(3)

            if period == "pm" and hour != 12:
                hour += 12
            elif period == "am" and hour == 12:
                hour = 0

            return f"{hour:02d}:{minute:02d}"

        # Match 13:00, 09:30
        match_24 = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", text_lower)

        if match_24:
            hour = int(match_24.group(1))
            minute = int(match_24.group(2))
            return f"{hour:02d}:{minute:02d}"

        return None
    
    def _is_explicit_list_request(self, user_message: str) -> bool:
        text = user_message.lower()

        explicit_list_phrases = [
            "show my",
            "show all",
            "show meetings",
            "show scheduled",
            "list my",
            "list all",
            "list meetings",
            "list scheduled",
            "check my schedule",
            "check the schedule",
            "check scheduled",
            "view my",
            "view meetings",
            "view scheduled",
            "scheduled meetings",
            "scheduled events",
            "my bookings",
            "my meetings",
        ]

        return any(phrase in text for phrase in explicit_list_phrases)


agent_service = AgentService()