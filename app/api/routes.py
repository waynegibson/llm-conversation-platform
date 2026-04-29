from fastapi import APIRouter

from api.v1.conversations import router as conversations_router
from api.v1.health import router as health_router
from api.v1.messages import router as messages_router
from api.v1.models import router as models_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(conversations_router, prefix="/api/v1", tags=["conversations"])
api_router.include_router(messages_router, prefix="/api/v1", tags=["messages"])
api_router.include_router(models_router, prefix="/api/v1", tags=["models"])
