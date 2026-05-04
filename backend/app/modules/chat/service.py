import uuid

from app.modules.chat.schemas import ChatRequest, ChatResponse
from app.modules.agent.service import agent_service

class ChatService:
    def handle_chat(self, request: ChatRequest) -> ChatResponse:
        user_message = request.message.strip()

        if not user_message:
            return ChatResponse(
                reply="Please enter a message.",
                session_id=request.session_id or str(uuid.uuid4()),
            )

        session_id = request.session_id or str(uuid.uuid4())

        reply = agent_service.chat(
            user_message=user_message,
            session_id=session_id,
        )

        return ChatResponse(
            reply=reply,
            session_id=session_id,
        )

chat_service = ChatService()