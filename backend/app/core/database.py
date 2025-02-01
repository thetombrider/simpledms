from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .config import get_settings
from ..models.document import Document

async def init_db():
    """Initialize database connection"""
    settings = get_settings()
    
    # Create Motor client
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    # Initialize beanie with the document models
    await init_beanie(
        database=client[settings.MONGODB_DB_NAME],
        document_models=[
            Document,
            # Add more models here as they are created
        ]
    )
    
    return client 