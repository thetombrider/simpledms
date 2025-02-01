from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .config import settings
from ..models.document import Document

async def init_db():
    """Initialize database connection and Beanie ODM"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client[settings.MONGODB_DB_NAME],
        document_models=[Document]
    ) 