from uuid import UUID

from models.entities import Conversation
from sqlalchemy import func, select
from sqlalchemy.orm import Session


class ConversationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, title: str | None, user_id: UUID | None, metadata: dict) -> Conversation:
        conversation = Conversation(title=title, user_id=user_id, metadata_json=metadata)
        self.db.add(conversation)
        self.db.flush()
        return conversation

    def get(self, conversation_id: UUID) -> Conversation | None:
        return self.db.get(Conversation, conversation_id)

    def list(self, limit: int, offset: int) -> list[Conversation]:
        return (
            self.db.execute(
                select(Conversation)
                .order_by(Conversation.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )
            .scalars()
            .all()
        )

    def count(self) -> int:
        return self.db.execute(select(func.count()).select_from(Conversation)).scalar_one()
