from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from schemas.message import ChatRequest, ChatResponse, MessageListResponse
from services.message_service import MessageService

from api.deps import get_message_service

router = APIRouter(prefix="/conversations/{conversation_id}/messages")


@router.get("", response_model=MessageListResponse)
def list_messages(
    conversation_id: UUID,
    service: MessageService = Depends(get_message_service),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> MessageListResponse:
    return service.list_messages(conversation_id=conversation_id, limit=limit, offset=offset)


@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
def create_chat_message(
    conversation_id: UUID,
    payload: ChatRequest,
    service: MessageService = Depends(get_message_service),
) -> object:
    if payload.stream:
        stream = service.create_chat_message_stream(
            conversation_id=conversation_id, payload=payload
        )
        return StreamingResponse(stream, media_type="text/event-stream")

    return service.create_chat_message(conversation_id=conversation_id, payload=payload)
