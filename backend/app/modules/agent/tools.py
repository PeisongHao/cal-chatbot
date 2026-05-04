from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo
import json
from langchain.tools import tool

from app.core.config import settings
from app.modules.cal.schemas import CreateBookingRequest, AttendeeInput
from app.modules.cal.service import cal_service


@tool
def create_cal_booking(
    name: str,
    email: str,
    date: str,
    time: str,
    reason: Optional[str] = None,
    timezone: Optional[str] = None,
) -> str:
    """
    Create a Cal.com booking for a user.

    Args:
        name: Attendee name.
        email: Attendee email.
        date: Meeting date in YYYY-MM-DD format.
        time: Meeting time in HH:MM 24-hour format.
        reason: Meeting reason.
        timezone: Attendee timezone. Default is backend CAL_TIMEZONE.
    """

    try:
        user_timezone = timezone or settings.CAL_TIMEZONE

        # Convert local date/time to UTC ISO format required by Cal.com
        local_dt = datetime.fromisoformat(f"{date}T{time}:00")
        local_dt = local_dt.replace(tzinfo=ZoneInfo(user_timezone))
        utc_dt = local_dt.astimezone(ZoneInfo("UTC"))
        start_utc = utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        booking_request = CreateBookingRequest(
            start=start_utc,
            attendee=AttendeeInput(
                name=name,
                email=email,
                timeZone=user_timezone,
                language="en",
            ),
            metadata={
                "reason": reason or "Meeting booked from AI chatbot"
            },
        )

        result = cal_service.create_booking(booking_request)

        if not result.get("success"):
            data = result.get("data", {})
            error_text = data.get("error")

            clean_message = result.get("message", "Failed to create booking.")

            if error_text:
                try:
                    error_json = json.loads(error_text)
                    clean_message = (
                        error_json
                        .get("error", {})
                        .get("message", clean_message)
                    )
                except Exception:
                    clean_message = error_text

            return clean_message

        data = result.get("data", {})
        booking_data = data.get("data", {})

        return (
            "Booking created successfully.\n"
            f"UID: {booking_data.get('uid')}\n"
            f"Title: {booking_data.get('title')}\n"
            f"Start: {booking_data.get('start')}\n"
            f"End: {booking_data.get('end')}\n"
            f"Status: {booking_data.get('status')}"
        )

    except Exception as e:
        return f"Unexpected error while creating booking: {str(e)}"
    
@tool
def list_cal_bookings_by_email(email: str) -> str:
    """
    List Cal.com bookings for a specific attendee email.

    Args:
        email: Attendee email address.
    """

    try:
        result = cal_service.list_bookings(email=email)

        if not result.get("success"):
            data = result.get("data", {})
            error_text = data.get("error")

            clean_message = result.get("message", "Failed to create booking.")

            if error_text:
                try:
                    error_json = json.loads(error_text)
                    clean_message = (
                        error_json
                        .get("error", {})
                        .get("message", clean_message)
                    )
                except Exception:
                    clean_message = error_text

            return clean_message

        bookings = result.get("bookings", [])

        if not bookings:
            return f"No bookings found for {email}."

        lines = [f"Found {len(bookings)} booking(s) for {email}:"]

        for index, booking in enumerate(bookings, start=1):
            attendee_text = ""

            if booking.attendees:
                attendee_names = [
                    attendee.name or attendee.email
                    for attendee in booking.attendees
                    if attendee.name or attendee.email
                ]
                attendee_text = ", ".join(attendee_names)

            lines.append(
                "\n"
                f"{index}. Meeting with {attendee_text or email}\n"
                f"   UID: {booking.uid}\n"
                f"   Status: {booking.status}\n"
                f"   Start: {booking.start}\n"
                f"   End: {booking.end}\n"
                f"   Duration: {booking.duration} minutes\n"
                f"   Location: {booking.location or booking.meetingUrl or 'N/A'}\n"
                f"   Attendees: {attendee_text or 'N/A'}"
            )

        return "\n".join(lines)

    except Exception as e:
        return f"Unexpected error while listing bookings: {str(e)}"