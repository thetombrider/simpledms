import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional
from ..services.share import ShareService

logger = logging.getLogger(__name__)

class BackgroundTasks:
    def __init__(self):
        self.share_service = ShareService()
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start_cleanup_task(self):
        """Start the periodic cleanup task"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._run_cleanup())
            logger.info("Started share cleanup task")
    
    async def stop_cleanup_task(self):
        """Stop the cleanup task"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped share cleanup task")
    
    async def _run_cleanup(self):
        """Run periodic cleanup of expired shares"""
        while True:
            try:
                # Run cleanup every hour
                deleted_count = await self.share_service.cleanup_expired_shares()
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired shares")
                
                # Wait for next cleanup cycle
                await asyncio.sleep(3600)  # 1 hour
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")
                # Wait a bit before retrying on error
                await asyncio.sleep(300)  # 5 minutes 