from typing import BinaryIO, Optional, Dict, Union
from fastapi import HTTPException
import boto3
from botocore.exceptions import ClientError
import io
from .base import StorageProvider

class S3StorageProvider(StorageProvider):
    """S3 implementation of storage provider"""
    
    def __init__(self, access_key: str, secret_key: str, bucket_name: str, region: str):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        self.bucket_name = bucket_name
    
    async def upload_file(self, file: Union[BinaryIO, bytes], file_path: str) -> str:
        try:
            # Convert to BytesIO if bytes
            if isinstance(file, bytes):
                file = io.BytesIO(file)
            
            # Upload file
            self.s3.upload_fileobj(file, self.bucket_name, file_path)
            return file_path
            
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error uploading file to S3: {str(e)}"
            )
    
    async def download_file(self, file_path: str) -> BinaryIO:
        try:
            output = io.BytesIO()
            self.s3.download_fileobj(self.bucket_name, file_path, output)
            output.seek(0)
            return output
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise HTTPException(status_code=404, detail="File not found")
            raise HTTPException(
                status_code=500,
                detail=f"Error downloading file from S3: {str(e)}"
            )
    
    async def delete_file(self, file_path: str) -> None:
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=file_path)
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting file from S3: {str(e)}"
            )
    
    async def generate_download_url(self, file_path: str, duration_in_seconds: int = 3600) -> str:
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_path
                },
                ExpiresIn=duration_in_seconds
            )
            return url
            
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating download URL: {str(e)}"
            )
    
    async def get_file_info(self, file_path: str) -> Dict:
        try:
            response = self.s3.head_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            return {
                "file_name": file_path.split('/')[-1],
                "content_type": response.get('ContentType'),
                "content_length": response.get('ContentLength'),
                "upload_timestamp": response.get('LastModified')
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                raise HTTPException(status_code=404, detail="File not found")
            raise HTTPException(
                status_code=500,
                detail=f"Error getting file info: {str(e)}"
            )
