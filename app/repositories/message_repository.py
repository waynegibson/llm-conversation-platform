from uuid import UUID

from models.entities import Message
from sqlalchemy import func, select
from sqlalchemy.orm import Session


class MessageRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, **kwargs) -> Message:
        message = Message(**kwargs)
        self.db.add(message)
        self.db.flush()
        return message

    def list_by_conversation(self, conversation_id: UUID, limit: int, offset: int) -> list[Message]:
        return (
            self.db.execute(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.asc())
                .limit(limit)
                .offset(offset)
            )
            .scalars()
            .all()
        )

    def count_by_conversation(self, conversation_id: UUID) -> int:
        return self.db.execute(
            select(func.count())
            .select_from(Message)
            .where(Message.conversation_id == conversation_id)
        ).scalar_one()

    def history_for_context(self, conversation_id: UUID) -> list[Message]:
        return (
            self.db.execute(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.asc(), Message.id.asc())
            )
            .scalars()
            .all()
        )
