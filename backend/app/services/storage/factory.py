from typing import Optional
import logging
import re
from .base import StorageProvider
from .b2 import B2StorageProvider
from .s3 import S3StorageProvider
from ...core.config import settings

# Get logger
logger = logging.getLogger(__name__)

class StorageFactory:
    """Factory for creating storage provider instances"""
    
    @staticmethod
    def _clean_value(value: str) -> str:
        """Clean a configuration value by removing comments and whitespace"""
        # Remove any inline comments (# or ; followed by text)
        value = re.sub(r'[#;].*$', '', value, flags=re.MULTILINE)
        # Remove quotes and whitespace
        value = value.strip().strip('"\'')
        return value
    
    @staticmethod
    def get_provider(
        provider_type: str,
        settings_dict: Optional[dict] = None
    ) -> StorageProvider:
        """Get a storage provider instance"""
        # Clean provider type
        provider = StorageFactory._clean_value(provider_type)
        logger.debug(f"Initializing storage provider of type: {provider}")
        settings_dict = settings_dict or {}
        
        try:
            if provider == "b2":
                logger.debug("Creating B2 storage provider")
                # Only log non-sensitive settings in trace level
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("B2 settings: %s", {
                        'bucket_name': settings_dict.get('bucket_name') or settings.B2_BUCKET_NAME
                    })
                
                return B2StorageProvider(
                    key_id=settings_dict.get('key_id') or settings.B2_KEY_ID,
                    app_key=settings_dict.get('app_key') or settings.B2_APPLICATION_KEY,
                    bucket_name=settings_dict.get('bucket_name') or settings.B2_BUCKET_NAME
                )
                
            elif provider == "s3":
                logger.debug("Creating S3 storage provider")
                # Only log non-sensitive settings in trace level
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("S3 settings: %s", {
                        'region': settings_dict.get('region') or settings.AWS_REGION,
                        'bucket_name': settings_dict.get('bucket_name') or settings.S3_BUCKET_NAME
                    })
                
                return S3StorageProvider(
                    access_key=settings_dict.get('access_key') or settings.AWS_ACCESS_KEY_ID,
                    secret_key=settings_dict.get('secret_key') or settings.AWS_SECRET_ACCESS_KEY,
                    bucket_name=settings_dict.get('bucket_name') or settings.S3_BUCKET_NAME,
                    region=settings_dict.get('region') or settings.AWS_REGION
                )
            else:
                error_msg = f"Unknown storage provider type: {provider}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
        except Exception as e:
            logger.error(f"Error creating storage provider: {str(e)}", exc_info=True)
            raise

def get_storage_provider() -> StorageProvider:
    """Get the configured storage provider"""
    provider = StorageFactory._clean_value(settings.STORAGE_PROVIDER)
    logger.debug(f"Getting storage provider from configuration: {provider}")
    return StorageFactory.get_provider(provider)
