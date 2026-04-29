from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from schemas.conversation import (
    ConversationCreate,
    ConversationListResponse,
    ConversationRead,
)
from services.conversation_service import ConversationService

from api.deps import get_conversation_service

router = APIRouter(prefix="/conversations")


@router.post("", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
def create_conversation(
    payload: ConversationCreate,
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationRead:
    return service.create_conversation(payload)


@router.get("", response_model=ConversationListResponse)
def list_conversations(
    service: ConversationService = Depends(get_conversation_service),
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> ConversationListResponse:
    return service.list_conversations(limit=limit, offset=offset)


@router.get("/{conversation_id}", response_model=ConversationRead)
def get_conversation(
    conversation_id: UUID,
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationRead:
    return service.get_conversation_or_404(conversation_id)
