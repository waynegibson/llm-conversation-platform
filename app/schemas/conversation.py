from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    user_id: UUID | None = None
    metadata: dict = Field(default_factory=dict)


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    user_id: UUID | None
    title: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    metadata: dict = Field(alias="metadata_json")


class ConversationListResponse(BaseModel):
    items: list[ConversationRead]
    total: int
