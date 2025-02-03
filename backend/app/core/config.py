from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path
import logging
import re

# Get the root directory (two levels up from this file)
ROOT_DIR = Path(__file__).parent.parent.parent.parent

# Valid storage providers
VALID_STORAGE_PROVIDERS = ["b2", "s3"]

# Valid log levels
VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

class Settings(BaseSettings):
    PROJECT_NAME: str = "SimpleS3DMS"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    
    # MongoDB settings
    MONGODB_URL: str = "mongodb://mongodb:27017"  # Default for Docker
    MONGODB_DB_NAME: str = "simpledms"
    ENVIRONMENT: str = "development"
    
    # Storage Provider settings
    STORAGE_PROVIDER: str = "b2"
    
    # B2 settings
    B2_KEY_ID: Optional[str] = None
    B2_APPLICATION_KEY: Optional[str] = None
    B2_BUCKET_NAME: Optional[str] = None
    
    # AWS S3 settings
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = None
    S3_BUCKET_NAME: Optional[str] = None
    
    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = None
    
    # JWT Settings
    SECRET_KEY: str = "development_secret_key_please_change_in_production"  # Default value for development
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8501",  # Streamlit default port
        "http://localhost:8080",  # Backend API port
        "http://127.0.0.1:8501",
        "http://127.0.0.1:8080",
    ]
    
    # AI settings
    ANTHROPIC_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ROOT_DIR / ".env"
        case_sensitive = True

    def _clean_value(self, value: str) -> str:
        """Clean a configuration value by removing comments and whitespace"""
        # Remove any inline comments (# or ; followed by text)
        value = re.sub(r'[#;].*$', '', value, flags=re.MULTILINE)
        # Remove quotes and whitespace
        value = value.strip().strip('"\'')
        return value

    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        # Clean and validate log level
        log_level_raw = self._clean_value(self.LOG_LEVEL)
        log_level = log_level_raw.upper()
        
        if log_level not in VALID_LOG_LEVELS:
            log_level = "INFO"
            print(f"Warning: Invalid log level '{log_level_raw}', defaulting to INFO")
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Get logger
        logger = logging.getLogger(__name__)
        logger.info(f"Logging level set to: {log_level}")
        return logger

    def validate_storage_config(self):
        """Validate storage configuration based on selected provider"""
        logger = logging.getLogger(__name__)
        logger.debug("Validating storage configuration")
        
        # Clean and validate storage provider
        raw_provider = self.STORAGE_PROVIDER
        provider = self._clean_value(raw_provider)
        logger.debug(f"Raw provider value: '{raw_provider}', cleaned: '{provider}'")
        
        if provider not in VALID_STORAGE_PROVIDERS:
            error_msg = (
                f"Invalid STORAGE_PROVIDER '{provider}'. "
                f"Must be one of: {', '.join(VALID_STORAGE_PROVIDERS)}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if provider == "b2":
            logger.debug("Validating B2 storage configuration")
            missing = []
            if not self._clean_value(str(self.B2_KEY_ID)):
                missing.append("B2_KEY_ID")
            if not self._clean_value(str(self.B2_APPLICATION_KEY)):
                missing.append("B2_APPLICATION_KEY")
            if not self._clean_value(str(self.B2_BUCKET_NAME)):
                missing.append("B2_BUCKET_NAME")
                
            if missing:
                error_msg = f"Missing required B2 settings: {', '.join(missing)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            logger.debug("B2 storage configuration is valid")
                
        elif provider == "s3":
            logger.debug("Validating S3 storage configuration")
            missing = []
            if not self._clean_value(str(self.AWS_ACCESS_KEY_ID)):
                missing.append("AWS_ACCESS_KEY_ID")
            if not self._clean_value(str(self.AWS_SECRET_ACCESS_KEY)):
                missing.append("AWS_SECRET_ACCESS_KEY")
            if not self._clean_value(str(self.AWS_REGION)):
                missing.append("AWS_REGION")
            if not self._clean_value(str(self.S3_BUCKET_NAME)):
                missing.append("S3_BUCKET_NAME")
                
            if missing:
                error_msg = f"Missing required S3 settings: {', '.join(missing)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            logger.debug("S3 storage configuration is valid")
        
        logger.debug("Storage configuration validation completed successfully")

@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.setup_logging()
    return settings

# Initialize settings
settings = Settings()
settings.setup_logging()
settings.validate_storage_config() 