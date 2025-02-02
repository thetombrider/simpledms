import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional
from ..services.share import ShareService
from ..services.document import DocumentService

logger = logging.getLogger(__name__)

class BackgroundTasks:
    def __init__(self):
        self.share_service = ShareService()
        self.document_service = DocumentService()
        self.cleanup_task = None
        self.running = False
    
    async def cleanup_expired_shares(self):
        """Clean up expired share links"""
        try:
            count = await self.share_service.cleanup_expired_shares()
            if count > 0:
                logger.info(f"Cleaned up {count} expired shares")
        except Exception as e:
            logger.error(f"Error cleaning up expired shares: {str(e)}")

    async def cleanup_orphaned_documents(self):
        """Clean up documents without B2 files"""
        try:
            count = await self.document_service.cleanup_orphaned_documents()
            if count > 0:
                logger.info(f"Cleaned up {count} orphaned documents")
        except Exception as e:
            logger.error(f"Error cleaning up orphaned documents: {str(e)}")
    
    async def cleanup_loop(self):
        """Main cleanup loop"""
        while self.running:
            await self.cleanup_expired_shares()
            await self.cleanup_orphaned_documents()
            await asyncio.sleep(3600)  # Run every hour
    
    async def start_cleanup_task(self):
        """Start the cleanup task"""
        self.running = True
        self.cleanup_task = asyncio.create_task(self.cleanup_loop())
        logger.info("Started background cleanup task")
    
    async def stop_cleanup_task(self):
        """Stop the cleanup task"""
        if self.running:
            self.running = False
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            logger.info("Stopped background cleanup task") 