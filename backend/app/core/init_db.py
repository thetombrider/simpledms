from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .config import settings
from ..models.document import Document
from ..models.category import Category
from ..models.tag import Tag
from ..models.share import Share

async def create_default_categories():
    """Create default categories if none exist"""
    if await Category.find_one() is None:  # Only create if no categories exist
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

async def init_db():
    """Initialize database connection and Beanie ODM"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client[settings.MONGODB_DB_NAME],
        document_models=[Document, Category, Tag, Share]
    )
    
    # Create default categories
    await create_default_categories() 