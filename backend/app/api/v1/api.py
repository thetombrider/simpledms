from fastapi import APIRouter
from backend.app.api.v1 import documents

api_router = APIRouter()
api_router.include_router(documents.router, prefix="/documents", tags=["documents"]) 