from repositories.model_repository import ModelRepository
from schemas.model import ModelListResponse
from sqlalchemy.orm import Session

from services.ollama_service import OllamaService


class ModelService:
    def __init__(self, db: Session, ollama_service: OllamaService) -> None:
        self.db = db
        self.ollama_service = ollama_service
        self.models = ModelRepository(db)

    def _sync_ollama_models(self) -> None:
        remote_models = self.ollama_service.list_models()
        for model in remote_models:
            model_name = model.get("name")
            if not model_name:
                continue

            details = model.get("details") or {}
            existing = self.models.get_by_provider_and_name(
                provider="ollama", model_name=model_name
            )
            if existing is None:
                self.models.create(
                    provider="ollama",
                    model_name=model_name,
                    model_family=details.get("family"),
                    quantization=details.get("quantization_level"),
                    active=True,
                )
                continue

            existing.model_family = details.get("family") or existing.model_family
            existing.quantization = details.get("quantization_level") or existing.quantization
            existing.active = True

        self.db.commit()

    def list_models(self, sync: bool = False) -> ModelListResponse:
        if sync:
            self._sync_ollama_models()

        items = self.models.list_all()
        return ModelListResponse(models=items)
