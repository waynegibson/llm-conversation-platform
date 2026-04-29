from uuid import UUID

from fastapi import HTTPException, status
from repositories.conversation_repository import ConversationRepository
from schemas.conversation import ConversationCreate, ConversationListResponse
from sqlalchemy.orm import Session


class ConversationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.conversations = ConversationRepository(db)

    def create_conversation(self, payload: ConversationCreate):
        conversation = self.conversations.create(
            title=payload.title,
            user_id=payload.user_id,
            metadata=payload.metadata,
        )
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def list_conversations(self, limit: int, offset: int) -> ConversationListResponse:
        items = self.conversations.list(limit=limit, offset=offset)
        total = self.conversations.count()
        return ConversationListResponse(items=items, total=total)

    def get_conversation_or_404(self, conversation_id: UUID):
        conversation = self.conversations.get(conversation_id)
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )
        return conversation
