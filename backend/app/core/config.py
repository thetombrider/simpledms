from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "SimpleS3DMS"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "simpledms"
    
    # B2 settings
    B2_KEY_ID: str
    B2_APPLICATION_KEY: str
    B2_BUCKET_NAME: str
    
    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:8501"]  # Streamlit default port
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings() 

settings = Settings() 