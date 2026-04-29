from fastapi import APIRouter, Depends, HTTPException, status
from services.ollama_service import OllamaService
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.deps import get_db_session, get_ollama_service

router = APIRouter()


@router.get("/health")
def health_check(
    db: Session = Depends(get_db_session),
    ollama_service: OllamaService = Depends(get_ollama_service),
) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    if not ollama_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Ollama unavailable"
        )
    return {"status": "ok", "db": "ok", "ollama": "ok"}


@router.get("/ready")
def readiness_check(
    db: Session = Depends(get_db_session),
    ollama_service: OllamaService = Depends(get_ollama_service),
) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    if not ollama_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Ollama unavailable"
        )
    return {"status": "ready"}
