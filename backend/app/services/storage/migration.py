from typing import Optional, Dict, List
import asyncio
from fastapi import HTTPException
from ...models.document import Document
from .factory import StorageFactory
from ...core.config import settings
import logging

logger = logging.getLogger(__name__)

class StorageMigration:
    def __init__(
        self,
        source_provider: str,
        target_provider: str,
        source_config: Optional[Dict] = None,
        target_config: Optional[Dict] = None
    ):
        self.source = StorageFactory.get_provider(source_provider, source_config or {})
        self.target = StorageFactory.get_provider(target_provider, target_config or {})
        
    async def migrate_file(self, file_path: str) -> bool:
        """Migrate a single file between storage providers"""
        try:
            # Download from source
            file_data = await self.source.download_file(file_path)
            
            # Upload to target
            await self.target.upload_file(file_data, file_path)
            
            # Verify upload
            await self.target.get_file_info(file_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Error migrating file {file_path}: {str(e)}")
            return False
    
    async def migrate_document_files(self, batch_size: int = 10) -> Dict:
        """Migrate all document files between storage providers"""
        results = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "failed_files": []
        }
        
        try:
            # Process documents in batches
            async for doc in Document.find_all():
                results["total"] += 1
                
                try:
                    # Migrate file
                    success = await self.migrate_file(doc.s3_key)
                    
                    if success:
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                        results["failed_files"].append(doc.s3_key)
                        
                except Exception as e:
                    results["failed"] += 1
                    results["failed_files"].append(doc.s3_key)
                    logger.error(f"Error migrating document {doc.id}: {str(e)}")
                
                # Process in batches to avoid memory issues
                if results["total"] % batch_size == 0:
                    await asyncio.sleep(0.1)  # Small delay between batches
                    
        except Exception as e:
            logger.error(f"Error during migration: {str(e)}")
            
        return results
    
    async def verify_migration(self) -> Dict:
        """Verify all files were migrated correctly"""
        results = {
            "total": 0,
            "verified": 0,
            "missing": 0,
            "missing_files": []
        }
        
        async for doc in Document.find_all():
            results["total"] += 1
            
            try:
                # Check if file exists in target storage
                await self.target.get_file_info(doc.s3_key)
                results["verified"] += 1
                
            except HTTPException as e:
                if e.status_code == 404:
                    results["missing"] += 1
                    results["missing_files"].append(doc.s3_key)
                    
            except Exception as e:
                logger.error(f"Error verifying file {doc.s3_key}: {str(e)}")
                results["missing"] += 1
                results["missing_files"].append(doc.s3_key)
        
        return results 