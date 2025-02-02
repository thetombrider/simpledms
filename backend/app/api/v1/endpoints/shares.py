from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime, timezone
from ....services.share import ShareService
from ....models.share import Share
import logging

router = APIRouter()
share_service = ShareService()
logger = logging.getLogger(__name__)

class ShareCreate(BaseModel):
    document_id: str
    owner_id: str
    expires_in_days: Optional[int] = 7

class ShareResponse(BaseModel):
    id: str
    document_id: str
    owner_id: str
    short_url: str
    expires_at: str

    class Config:
        json_encoders = {
            ObjectId: str
        }

@router.post("/", response_model=ShareResponse)
async def create_share(share: ShareCreate):
    """Create a new share link for a document"""
    try:
        result = await share_service.create_share(
            share.document_id,
            share.owner_id,
            share.expires_in_days
        )
        return {
            "id": str(result.id),
            "document_id": str(result.document_id),
            "owner_id": result.owner_id,
            "short_url": result.short_url,
            "expires_at": result.expires_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{share_id}", response_model=ShareResponse)
async def get_share(share_id: str):
    """Get share details"""
    try:
        share = await share_service.get_share(share_id)
        return {
            "id": str(share.id),
            "document_id": str(share.document_id),
            "owner_id": share.owner_id,
            "short_url": share.short_url,
            "expires_at": share.expires_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{owner_id}", response_model=List[ShareResponse])
async def list_shares(
    owner_id: str,
    include_expired: bool = False
):
    """List all shares for a user"""
    try:
        shares = await share_service.list_shares(owner_id, include_expired)
        return [
            {
                "id": str(share.id),
                "document_id": str(share.document_id),
                "owner_id": share.owner_id,
                "short_url": share.short_url,
                "expires_at": share.expires_at.isoformat()
            }
            for share in shares
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing shares: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error listing shares: {str(e)}"
        )

@router.delete("/{share_id}")
async def delete_share(share_id: str, owner_id: str):
    """Delete a share"""
    try:
        await share_service.delete_share(share_id, owner_id)
        return {"message": "Share deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 