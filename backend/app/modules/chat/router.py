from fastapi import APIRouter

from app.modules.chat.schemas import ChatRequest, ChatResponse
from app.modules.chat.service import chat_service


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    return chat_service.handle_chat(request)