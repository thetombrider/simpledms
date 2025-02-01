from typing import Optional, List
from beanie import Document
from pydantic import Field, ConfigDict
from datetime import datetime
from .base import BaseDocument

class Document(BaseDocument):
    """Document model for storing file metadata"""
    
    title: str = Field(index=True)
    description: Optional[str] = None
    file_name: str
    file_size: int
    mime_type: str
    s3_key: str  # S3 object key
    categories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    owner_id: str = Field(index=True)  # Reference to user ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "documents"
        indexes = [
            "title",
            "owner_id",
            "categories",
            "tags"
        ]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Invoice 2024-001",
                "description": "January 2024 invoice",
                "file_name": "invoice_2024_001.pdf",
                "file_size": 1024567,
                "mime_type": "application/pdf",
                "s3_key": "documents/2024/01/invoice_2024_001.pdf",
                "categories": ["invoices", "finance"],
                "tags": ["2024", "january", "paid"],
                "owner_id": "user123"
            }
        }
    ) 