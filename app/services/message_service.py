import json
import time
from collections.abc import Iterator
from uuid import UUID

from fastapi import HTTPException, status
from observability.metrics import CHAT_REQUESTS
from repositories.conversation_repository import ConversationRepository
from repositories.message_repository import MessageRepository
from repositories.model_repository import ModelRepository
from schemas.message import ChatRequest, ChatResponse, MessageListResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from services.ollama_service import OllamaService
from services.token_counter import trim_history_by_token_budget


class MessageService:
    def __init__(self, db: Session, ollama_service: OllamaService) -> None:
        self.db = db
        self.ollama_service = ollama_service
        self.conversations = ConversationRepository(db)
        self.messages = MessageRepository(db)
        self.models = ModelRepository(db)

    def list_messages(self, conversation_id: UUID, limit: int, offset: int) -> MessageListResponse:
        conversation = self.conversations.get(conversation_id)
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        items = self.messages.list_by_conversation(
            conversation_id=conversation_id, limit=limit, offset=offset
        )
        total = self.messages.count_by_conversation(conversation_id=conversation_id)
        return MessageListResponse(items=items, total=total)

    def create_chat_message(self, conversation_id: UUID, payload: ChatRequest) -> ChatResponse:
        conversation = self.conversations.get(conversation_id)
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        CHAT_REQUESTS.labels(mode="non_stream").inc()

        db_model = self.models.get_or_create_active_ollama_model(payload.model_name)

        user_message = self.messages.create(
            conversation_id=conversation_id,
            model_id=db_model.id,
            role="user",
            content=payload.content,
            temperature=payload.temperature,
            top_p=payload.top_p,
        )

        history = self.messages.history_for_context(conversation_id=conversation_id)
        context_window = db_model.context_window or 4096
        token_budget = int(context_window * 0.8)
        trimmed_history = trim_history_by_token_budget(history, token_budget=token_budget)
        ollama_messages = [{"role": item.role, "content": item.content} for item in trimmed_history]

        result = self.ollama_service.chat(
            model_name=payload.model_name,
            messages=ollama_messages,
            temperature=payload.temperature,
            top_p=payload.top_p,
            stream=False,
        )

        assistant_message = self.messages.create(
            conversation_id=conversation_id,
            model_id=db_model.id,
            role="assistant",
            content=result["content"],
            prompt_tokens=result["prompt_tokens"],
            completion_tokens=result["completion_tokens"],
            total_tokens=result["total_tokens"],
            latency_ms=result["latency_ms"],
            temperature=payload.temperature,
            top_p=payload.top_p,
            request_payload=result["request_payload"],
            response_payload=result["response_payload"],
        )

        conversation.updated_at = func.now()
        self.db.commit()
        self.db.refresh(user_message)
        self.db.refresh(assistant_message)

        return ChatResponse(user_message=user_message, assistant_message=assistant_message)

    def create_chat_message_stream(
        self, conversation_id: UUID, payload: ChatRequest
    ) -> Iterator[str]:
        conversation = self.conversations.get(conversation_id)
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        CHAT_REQUESTS.labels(mode="stream").inc()

        db_model = self.models.get_or_create_active_ollama_model(payload.model_name)
        user_message = self.messages.create(
            conversation_id=conversation_id,
            model_id=db_model.id,
            role="user",
            content=payload.content,
            temperature=payload.temperature,
            top_p=payload.top_p,
        )
        self.db.commit()
        self.db.refresh(user_message)

        history = self.messages.history_for_context(conversation_id=conversation_id)
        context_window = db_model.context_window or 4096
        token_budget = int(context_window * 0.8)
        trimmed_history = trim_history_by_token_budget(history, token_budget=token_budget)
        ollama_messages = [{"role": item.role, "content": item.content} for item in trimmed_history]

        def event_stream() -> Iterator[str]:
            started = time.perf_counter()
            chunks: list[str] = []
            final_payload: dict | None = None

            try:
                for chunk in self.ollama_service.chat_stream(
                    model_name=payload.model_name,
                    messages=ollama_messages,
                    temperature=payload.temperature,
                    top_p=payload.top_p,
                ):
                    message_content = (chunk.get("message") or {}).get("content") or ""
                    if message_content:
                        chunks.append(message_content)
                        yield f"data: {json.dumps({'type': 'token', 'content': message_content})}\n\n"

                    if chunk.get("done"):
                        final_payload = chunk

                assistant_content = "".join(chunks)
                latency_ms = int((time.perf_counter() - started) * 1000)
                prompt_tokens = (final_payload or {}).get("prompt_eval_count")
                completion_tokens = (final_payload or {}).get("eval_count")
                total_tokens = (prompt_tokens or 0) + (completion_tokens or 0)

                assistant_message = self.messages.create(
                    conversation_id=conversation_id,
                    model_id=db_model.id,
                    role="assistant",
                    content=assistant_content,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    latency_ms=latency_ms,
                    temperature=payload.temperature,
                    top_p=payload.top_p,
                    request_payload={
                        "model": payload.model_name,
                        "messages": ollama_messages,
                        "stream": True,
                    },
                    response_payload=final_payload,
                )

                conversation.updated_at = func.now()
                self.db.commit()
                self.db.refresh(assistant_message)

                done_event = {
                    "type": "done",
                    "assistant_message_id": str(assistant_message.id),
                    "total_tokens": total_tokens,
                    "latency_ms": latency_ms,
                }
                yield f"data: {json.dumps(done_event)}\n\n"
            except Exception as exc:
                self.db.rollback()
                error_event = {"type": "error", "message": str(exc)}
                yield f"data: {json.dumps(error_event)}\n\n"

        return event_stream()
