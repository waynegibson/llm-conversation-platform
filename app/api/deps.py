from collections.abc import Generator

from db.session import get_db
from fastapi import Depends
from services.conversation_service import ConversationService
from services.message_service import MessageService
from services.model_service import ModelService
from services.ollama_service import OllamaService
from sqlalchemy.orm import Session


def get_db_session() -> Generator[Session, None, None]:
    yield from get_db()


def get_ollama_service() -> OllamaService:
    return OllamaService()


def get_conversation_service(db: Session = Depends(get_db_session)) -> ConversationService:
    return ConversationService(db)


def get_message_service(
    db: Session = Depends(get_db_session),
    ollama_service: OllamaService = Depends(get_ollama_service),
) -> MessageService:
    return MessageService(db=db, ollama_service=ollama_service)


def get_model_service(
    db: Session = Depends(get_db_session),
    ollama_service: OllamaService = Depends(get_ollama_service),
) -> ModelService:
    return ModelService(db=db, ollama_service=ollama_service)
