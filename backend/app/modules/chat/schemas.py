from typing import Optional
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(
        default=None,
        description="Conversation session id"
    )

class ChatResponse(BaseModel):
    reply: str
    session_id: str