from fastapi import APIRouter, Depends
from schemas.model import ModelListResponse
from services.model_service import ModelService

from api.deps import get_model_service

router = APIRouter(prefix="/models")


@router.get("", response_model=ModelListResponse)
def list_models(
    sync: bool = False,
    service: ModelService = Depends(get_model_service),
) -> ModelListResponse:
    return service.list_models(sync=sync)
