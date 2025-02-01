from typing import BinaryIO, Optional, Union
from fastapi import HTTPException
from b2sdk.v2 import B2Api, InMemoryAccountInfo, Bucket
from b2sdk.v2.exception import B2Error, FileNotPresent
from ..core.config import get_settings, settings
import io

class B2Service:
    """Service for interacting with Backblaze B2"""
    def __init__(self):
        # Initialize B2 API with in-memory account info
        self.info = InMemoryAccountInfo()
        self.api = B2Api(self.info)
        
        # Authenticate
        self.api.authorize_account("production", settings.B2_KEY_ID, settings.B2_APPLICATION_KEY)
        
        # Get bucket
        self.bucket = self.api.get_bucket_by_name(settings.B2_BUCKET_NAME)

    async def upload_file(self, file: Union[BinaryIO, bytes], file_path: str) -> str:
        """Upload a file to B2"""
        try:
            # Convert to bytes if not already
            if isinstance(file, (io.BytesIO, io.BufferedReader)):
                file_content = file.read()
            else:
                file_content = file
            
            # Upload the file
            uploaded_file = self.bucket.upload_bytes(
                file_content,
                file_path
            )
            
            return uploaded_file.file_name
            
        except B2Error as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error uploading file to B2: {str(e)}"
            )

    async def download_file(self, file_path: str) -> BinaryIO:
        """Download a file from B2"""
        try:
            # Download file into memory
            output = io.BytesIO()
            downloaded = self.bucket.download_file_by_name(file_path)
            downloaded.save(output)
            output.seek(0)  # Reset the buffer position to the beginning
            return output
            
        except FileNotPresent:
            raise HTTPException(status_code=404, detail="File not found")
        except B2Error as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error downloading file from B2: {str(e)}"
            )

    async def delete_file(self, file_path: str) -> None:
        """Delete a file from B2"""
        try:
            # Get file info
            file_version = self.bucket.get_file_info_by_name(file_path)
            # Delete the file
            self.bucket.delete_file_version(file_version.id_, file_version.file_name)
            
        except FileNotPresent:
            raise HTTPException(status_code=404, detail="File not found")
        except B2Error as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting file from B2: {str(e)}"
            )

    async def generate_download_url(self, file_path: str, duration_in_seconds: int = 3600) -> str:
        """Generate a download URL for a file"""
        try:
            # Get file info
            file_version = self.bucket.get_file_info_by_name(file_path)
            
            # Get download authorization
            download_auth = self.bucket.get_download_authorization(
                file_name_prefix=file_path,
                valid_duration_in_seconds=duration_in_seconds
            )
            
            # Generate download URL with authorization
            url = self.api.get_download_url_for_file_name(
                bucket_name=self.bucket.name,
                file_name=file_path
            )
            
            # Add authorization to URL
            return f"{url}?Authorization={download_auth}"
            
        except FileNotPresent:
            raise HTTPException(status_code=404, detail="File not found")
        except B2Error as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating download URL: {str(e)}"
            ) 