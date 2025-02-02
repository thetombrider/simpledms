from fastapi import APIRouter
from . import documents, categories, tags, shares

api_router = APIRouter()
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(categories.router, prefix="/config/categories", tags=["categories"])
api_router.include_router(tags.router, prefix="/config/tags", tags=["tags"])
api_router.include_router(shares.router, prefix="/shares", tags=["shares"]) 