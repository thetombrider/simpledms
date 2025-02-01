from beanie import Document
from pydantic import Field
from typing import Optional
from .base import BaseDocument

class Category(BaseDocument):
    """Category model for document classification"""
    name: str = Field(unique=True, index=True)
    icon: str = Field(default="📄")  # Default document icon
    description: Optional[str] = None
    
    class Settings:
        name = "categories" 