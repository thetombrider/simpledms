from datetime import datetime, timezone
from bson import ObjectId
from pydantic import Field, ConfigDict, field_validator
from .base import BaseDocument

class Share(BaseDocument):
    """Share model for document sharing"""
    document_id: ObjectId = Field(index=True)
    owner_id: str = Field(index=True)
    short_url: str
    long_url: str
    expires_at: datetime = Field(index=True)
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }
    )
    
    @field_validator('expires_at')
    @classmethod
    def ensure_timezone(cls, v: datetime) -> datetime:
        """Ensure datetime is timezone-aware"""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v
    
    class Settings:
        name = "shares"
        indexes = [
            "document_id",
            "owner_id",
            "expires_at"
        ] 