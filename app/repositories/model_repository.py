from models.entities import LLMModel
from sqlalchemy import select
from sqlalchemy.orm import Session


class ModelRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[LLMModel]:
        return (
            self.db.execute(select(LLMModel).order_by(LLMModel.created_at.desc())).scalars().all()
        )

    def get_by_provider_and_name(self, provider: str, model_name: str) -> LLMModel | None:
        return (
            self.db.execute(
                select(LLMModel).where(
                    LLMModel.provider == provider,
                    LLMModel.model_name == model_name,
                )
            )
            .scalars()
            .first()
        )

    def create(self, **kwargs) -> LLMModel:
        model = LLMModel(**kwargs)
        self.db.add(model)
        self.db.flush()
        return model

    def get_active_ollama_model(self, model_name: str) -> LLMModel | None:
        model = self.get_by_provider_and_name(provider="ollama", model_name=model_name)
        if model is None or not model.active:
            return None
        return model

    def create_ollama_model(self, model_name: str) -> LLMModel:
        return self.create(provider="ollama", model_name=model_name, active=True)

    def get_or_create_active_ollama_model(self, model_name: str) -> LLMModel:
        model = self.get_active_ollama_model(model_name)
        if model is None:
            model = self.create_ollama_model(model_name)
        return model
