from datetime import datetime
from typing import Optional
from beanie import Document, Indexed
from pydantic import BaseModel

class TimestampModel(BaseModel):
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

class BaseDocument(Document, TimestampModel):
    """Base document with timestamp fields"""
    
    class Settings:
        use_state_management = True
        
    def before_save(self) -> None:
        self.updated_at = datetime.utcnow()
        return super().before_save() 