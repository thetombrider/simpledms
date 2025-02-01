from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.init_db import init_db
from app.api.v1.endpoints.documents import router as documents_router
from app.api.v1.endpoints.categories import router as categories_router
from app.api.v1.endpoints.tags import router as tags_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "api_version": settings.VERSION}

# Include API routers
app.include_router(documents_router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(categories_router, prefix="/api/v1/config/categories", tags=["categories"])
app.include_router(tags_router, prefix="/api/v1/config/tags", tags=["tags"])

@app.on_event("startup")
async def startup_event():
    await init_db() 