from datetime import datetime, timedelta, timezone
import pyshorteners
from typing import Optional
from bson import ObjectId
import logging
import os
from ..models.document import Document
from ..models.share import Share
from .b2 import B2Service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShareService:
    def __init__(self):
        self.b2_service = B2Service()
        self.shortener = pyshorteners.Shortener()
        logger.info("ShareService initialized")
    
    async def create_share(
        self,
        document_id: str,
        owner_id: str,
        expires_in_days: Optional[int] = 7
    ) -> Share:
        """Create a new share link for a document"""
        try:
            logger.info(f"Creating share for document {document_id} by owner {owner_id}")
            
            # Get document
            doc_obj_id = ObjectId(document_id)
            document = await Document.get(doc_obj_id)
            
            if not document:
                logger.error(f"Document {document_id} not found")
                raise ValueError("Document not found")
            if document.owner_id != owner_id:
                logger.error(f"Access denied: {owner_id} does not own document {document_id}")
                raise ValueError("Access denied")
            
            # Generate B2 download URL
            long_url = await self.b2_service.generate_download_url(
                document.s3_key,
                duration_in_seconds=expires_in_days * 24 * 3600
            )
            
            # Create short URL using is.gd
            try:
                short_url = self.shortener.isgd.short(long_url)
                logger.info(f"Created short URL: {short_url}")
            except Exception as e:
                logger.warning(f"URL shortening failed: {str(e)}")
                logger.info("Using long URL as fallback")
                short_url = long_url
            
            # Create share record
            current_time = datetime.now(timezone.utc)
            expiry_time = current_time + timedelta(days=expires_in_days)
            
            share = Share(
                document_id=doc_obj_id,
                owner_id=owner_id,
                short_url=short_url,
                long_url=long_url,
                expires_at=expiry_time
            )
            
            # Save share
            await share.insert()
            logger.info(f"Share created successfully with ID: {share.id}")
            
            return share
            
        except ValueError as e:
            logger.error(f"ValueError in create_share: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_share: {str(e)}", exc_info=True)
            raise ValueError(f"Error creating share: {str(e)}")
    
    async def get_share(self, share_id: str) -> Share:
        """Get share by ID"""
        try:
            share = await Share.get(ObjectId(share_id))
            if not share:
                raise ValueError("Share not found")
            
            # Check if expired
            if share.expires_at < datetime.now(timezone.utc):
                await share.delete()
                raise ValueError("Share link has expired")
            
            return share
            
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Error getting share: {str(e)}")
    
    async def list_shares(
        self,
        owner_id: str,
        include_expired: bool = False
    ) -> list[Share]:
        """List all shares for a user"""
        try:
            query = Share.find(Share.owner_id == owner_id)
            if not include_expired:
                query = query.find(Share.expires_at > datetime.now(timezone.utc))
            return await query.to_list()
            
        except Exception as e:
            raise ValueError(f"Error listing shares: {str(e)}")
    
    async def delete_share(self, share_id: str, owner_id: str) -> None:
        """Delete a share"""
        try:
            share = await Share.get(ObjectId(share_id))
            if not share:
                raise ValueError("Share not found")
            if share.owner_id != owner_id:
                raise ValueError("Access denied")
            
            await share.delete()
            
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Error deleting share: {str(e)}")
    
    async def cleanup_expired_shares(self) -> int:
        """Delete all expired shares"""
        try:
            result = await Share.find(
                Share.expires_at < datetime.now(timezone.utc)
            ).delete()
            return result.deleted_count
            
        except Exception as e:
            raise ValueError(f"Error cleaning up expired shares: {str(e)}") 