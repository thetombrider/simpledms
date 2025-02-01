from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .config import get_settings
from ..models.document import Document
from ..models.category import Category
from ..models.tag import Tag

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
            Category,
            Tag
        ]
    )
    
    # Create default categories if none exist
    if await Category.find_one() is None:
        default_categories = [
            Category(name="Invoice", icon="📄", description="Invoice documents"),
            Category(name="Contract", icon="📝", description="Contract documents"),
            Category(name="Report", icon="📊", description="Report documents"),
            Category(name="Other", icon="📎", description="Other documents")
        ]
        for category in default_categories:
            try:
                await category.insert()
            except Exception:
                pass  # Skip if category already exists
    
    return client 