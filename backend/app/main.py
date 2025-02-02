from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from beanie import init_beanie
import logging

from .core.config import get_settings
from .core.database import init_db
from .core.tasks import BackgroundTasks
from .api.v1.endpoints import documents, config, categories, tags, shares
from .models.share import Share
from .models.document import Document
from .models.category import Category
from .models.tag import Tag

# Configure logging
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SimpleS3DMS API",
    description="API for SimpleS3DMS - A Simple Document Management System",
    version="0.1.0",
    openapi_url=f"{get_settings().API_V1_STR}/openapi.json"
)

# Configure CORS
settings = get_settings()
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Create background tasks instance
background_tasks = BackgroundTasks()

@app.on_event("startup")
async def startup_event():
    """Initialize database connection and start background tasks"""
    # Initialize MongoDB connection
    app.state.db_client = await init_db()
    
    # Initialize Beanie ODM with all models
    await init_beanie(
        database=app.state.db_client[get_settings().MONGODB_DB_NAME],
        document_models=[Document, Category, Tag, Share]
    )
    
    # Clean up any existing shares that might have old schema
    try:
        logger.info("Cleaning up old shares...")
        await Share.find({}).delete()
        logger.info("Old shares cleaned up")
    except Exception as e:
        logger.error(f"Error cleaning up old shares: {str(e)}")
    
    # Start background tasks
    await background_tasks.start_cleanup_task()

# Include API routes after database initialization
app.include_router(
    documents.router,
    prefix=f"{settings.API_V1_STR}/documents",
    tags=["documents"]
)

app.include_router(
    config.router,
    prefix=f"{settings.API_V1_STR}/config",
    tags=["config"]
)

app.include_router(
    categories.router,
    prefix=f"{settings.API_V1_STR}/categories",
    tags=["categories"]
)

app.include_router(
    tags.router,
    prefix=f"{settings.API_V1_STR}/tags",
    tags=["tags"]
)

app.include_router(
    shares.router,
    prefix=f"{settings.API_V1_STR}/shares",
    tags=["shares"]
)

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection and stop background tasks"""
    if hasattr(app.state, "db_client"):
        app.state.db_client.close()
    await background_tasks.stop_cleanup_task()

@app.get("/health")
async def health_check():
    """Check service health status"""
    try:
        # Check database connection
        await app.state.db_client.server_info()
        
        return {
            "status": "healthy",
            "database": "connected",
            "version": app.version,
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )

@app.get("/")
async def root():
    return {
        "message": "Welcome to SimpleS3DMS API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 