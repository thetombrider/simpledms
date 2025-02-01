from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from .core.config import get_settings
from .core.database import init_db
from .api.v1.endpoints import documents, config

app = FastAPI(
    title="SimpleS3DMS API",
    description="API for SimpleS3DMS - A Simple Document Management System",
    version="0.1.0"
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
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

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    app.state.db_client = await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    if hasattr(app.state, "db_client"):
        app.state.db_client.close()

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