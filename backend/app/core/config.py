from typing import List, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path

# Get the root directory (two levels up from this file)
ROOT_DIR = Path(__file__).parent.parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "SimpleS3DMS"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "simpledms"
    ENVIRONMENT: str = "development"
    
    # B2 settings
    B2_KEY_ID: str
    B2_APPLICATION_KEY: str
    B2_BUCKET_NAME: str
    
    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = None
    
    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8501",  # Streamlit default port
        "http://localhost:8080",  # Backend API port
        "http://127.0.0.1:8501",
        "http://127.0.0.1:8080",
    ]
    
    class Config:
        env_file = ROOT_DIR / ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings() 

settings = Settings() 