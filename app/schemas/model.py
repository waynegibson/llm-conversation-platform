from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ModelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    provider: str
    model_name: str
    model_tag: str | None
    model_family: str | None
    context_window: int | None
    quantization: str | None
    active: bool
    created_at: datetime


class ModelListResponse(BaseModel):
    models: list[ModelRead]
