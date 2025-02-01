from typing import Optional, List
from beanie import Indexed
from pydantic import Field
from .base import BaseDocument

class Document(BaseDocument):
    """Document model for storing file metadata"""
    
    title: Indexed(str)
    description: Optional[str] = None
    file_name: str
    file_size: int
    mime_type: str
    s3_key: str  # S3 object key
    categories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    owner_id: Indexed(str)  # Reference to user ID
    
    class Settings:
        name = "documents"
        indexes = [
            "title",
            "owner_id",
            "categories",
            "tags"
        ]
    
    class Config:
        schema_extra = {
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