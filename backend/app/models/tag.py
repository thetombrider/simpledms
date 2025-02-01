from beanie import Document
from pydantic import Field
from .base import BaseDocument

class Tag(BaseDocument):
    """Tag model for document classification"""
    name: str = Field(unique=True, index=True)
    color: str = Field(default="#808080")  # Default gray color
    
    class Settings:
        name = "tags" 