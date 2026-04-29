from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    model_name: str = Field(min_length=1, max_length=150)
    content: str = Field(min_length=1)
    temperature: float | None = Field(default=None, ge=0, le=2)
    top_p: float | None = Field(default=None, ge=0, le=1)
    stream: bool = False


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    model_id: UUID | None
    role: str
    content: str
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    latency_ms: int | None
    created_at: datetime


class MessageListResponse(BaseModel):
    items: list[MessageRead]
    total: int


class ChatResponse(BaseModel):
    user_message: MessageRead
    assistant_message: MessageRead
