from typing import BinaryIO, Optional, Dict, Union
from fastapi import HTTPException
from b2sdk.v2 import B2Api, InMemoryAccountInfo
from b2sdk.v2.exception import B2Error, FileNotPresent
import io
import logging
from .base import StorageProvider
from ...core.config import settings

# Get logger
logger = logging.getLogger(__name__)

class B2StorageProvider(StorageProvider):
    """B2 implementation of storage provider"""
    
    def __init__(self, key_id: str, app_key: str, bucket_name: str):
        logger.debug("Initializing B2 storage provider")
        try:
            # Initialize B2 API with in-memory account info
            self.info = InMemoryAccountInfo()
            self.api = B2Api(self.info)
            
            # Authenticate
            logger.debug("Authenticating with B2")
            self.api.authorize_account("production", key_id, app_key)
            
            # Get bucket
            logger.debug(f"Getting bucket: {bucket_name}")
            self.bucket = self.api.get_bucket_by_name(bucket_name)
            logger.debug("B2 storage provider initialized successfully")
            
        except B2Error as e:
            error_msg = f"Error initializing B2 storage: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise HTTPException(status_code=500, detail=error_msg)
    
    async def upload_file(self, file: Union[BinaryIO, bytes], file_path: str) -> str:
        try:
            logger.debug(f"Uploading file to B2: {file_path}")
            # Convert to bytes if not already
            if isinstance(file, (io.BytesIO, io.BufferedReader)):
                logger.debug("Converting file-like object to bytes")
                file_content = file.read()
            else:
                file_content = file
            
            # Upload the file
            uploaded_file = self.bucket.upload_bytes(
                file_content,
                file_path
            )
            
            logger.debug(f"Successfully uploaded file: {uploaded_file.file_name}")
            return uploaded_file.file_name
            
        except B2Error as e:
            error_msg = f"Error uploading file to B2: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )
    
    async def download_file(self, file_path: str) -> BinaryIO:
        try:
            logger.debug(f"Downloading file from B2: {file_path}")
            output = io.BytesIO()
            downloaded = self.bucket.download_file_by_name(file_path)
            downloaded.save(output)
            output.seek(0)
            logger.debug("File downloaded successfully")
            return output
            
        except FileNotPresent:
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)
        except B2Error as e:
            error_msg = f"Error downloading file from B2: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )
    
    async def delete_file(self, file_path: str) -> None:
        try:
            logger.debug(f"Deleting file from B2: {file_path}")
            file_version = self.bucket.get_file_info_by_name(file_path)
            self.bucket.delete_file_version(
                file_version.id_,
                file_version.file_name
            )
            logger.debug("File deleted successfully")
            
        except FileNotPresent:
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)
        except B2Error as e:
            error_msg = f"Error deleting file from B2: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )
    
    async def generate_download_url(self, file_path: str, duration_in_seconds: int = 3600) -> str:
        try:
            logger.debug(f"Generating download URL for file: {file_path}")
            clean_path = file_path.strip('[]')
            file_version = self.bucket.get_file_info_by_name(clean_path)
            
            download_auth = self.bucket.get_download_authorization(
                file_name_prefix=clean_path,
                valid_duration_in_seconds=duration_in_seconds
            )
            
            url = self.api.get_download_url_for_file_name(
                bucket_name=self.bucket.name,
                file_name=clean_path
            )
            
            final_url = f"{url}?Authorization={download_auth}"
            logger.debug("Download URL generated successfully")
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"URL valid for {duration_in_seconds} seconds")
            return final_url
            
        except FileNotPresent:
            error_msg = f"File not found: {clean_path}"
            logger.error(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)
        except B2Error as e:
            error_msg = f"Error generating download URL: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )
    
    async def get_file_info(self, file_path: str) -> Dict:
        try:
            logger.debug(f"Getting file info from B2: {file_path}")
            clean_path = file_path.strip('[]')
            file_version = self.bucket.get_file_info_by_name(clean_path)
            
            info = {
                "file_name": file_version.file_name,
                "content_type": file_version.content_type,
                "content_length": file_version.content_length,
                "upload_timestamp": file_version.upload_timestamp
            }
            logger.debug("File info retrieved successfully")
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"File info: {info}")
            return info
            
        except FileNotPresent:
            error_msg = f"File not found: {clean_path}"
            logger.error(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)
        except B2Error as e:
            error_msg = f"Error getting file info: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=error_msg
            ) 