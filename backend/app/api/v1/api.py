from fastapi import APIRouter
from backend.app.api.v1 import documents, config

api_router = APIRouter()
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(config.router, prefix="/config", tags=["config"]) 