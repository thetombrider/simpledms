import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from fastapi import HTTPException
from ..core.config import get_settings
from typing import BinaryIO
import io

class S3Service:
    def __init__(self):
        settings = get_settings()
        # Configure boto3 for B2 compatibility
        config = Config(
            s3={'addressing_style': 'virtual'}
        )
        
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f'https://{settings.S3_ENDPOINT_URL}',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=config
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    async def upload_file(self, file: BinaryIO, s3_key: str) -> str:
        """Upload a file to B2"""
        try:
            # Read the file content into memory
            file_content = file.read()
            # Use put_object for direct upload
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType='application/octet-stream'
            )
            return s3_key
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error uploading file to B2: {str(e)}"
            )

    async def download_file(self, s3_key: str) -> BinaryIO:
        """Download a file from B2"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return response['Body']
        except ClientError as e:
            raise HTTPException(
                status_code=404 if e.response['Error']['Code'] == 'NoSuchKey' else 500,
                detail=f"Error downloading file from B2: {str(e)}"
            )

    async def delete_file(self, s3_key: str) -> None:
        """Delete a file from B2"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting file from B2: {str(e)}"
            )

    async def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """Generate a presigned URL for file download"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating presigned URL: {str(e)}"
            ) 