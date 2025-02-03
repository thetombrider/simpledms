import asyncio
import argparse
from app.services.storage.migration import StorageMigration
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def migrate_storage(source: str, target: str, batch_size: int = 10):
    """Migrate files between storage providers"""
    logger.info(f"Starting migration from {source} to {target}")
    
    # Initialize migration
    migration = StorageMigration(source, target)
    
    # Migrate files
    logger.info("Migrating files...")
    results = await migration.migrate_document_files(batch_size)
    
    # Log results
    logger.info("Migration completed:")
    logger.info(f"Total files: {results['total']}")
    logger.info(f"Successfully migrated: {results['success']}")
    logger.info(f"Failed: {results['failed']}")
    
    if results['failed_files']:
        logger.warning("Failed files:")
        for file in results['failed_files']:
            logger.warning(f"  - {file}")
    
    # Verify migration
    logger.info("\nVerifying migration...")
    verification = await migration.verify_migration()
    
    logger.info("Verification completed:")
    logger.info(f"Total files: {verification['total']}")
    logger.info(f"Verified: {verification['verified']}")
    logger.info(f"Missing: {verification['missing']}")
    
    if verification['missing_files']:
        logger.warning("Missing files:")
        for file in verification['missing_files']:
            logger.warning(f"  - {file}")
    
    return results['failed'] == 0 and verification['missing'] == 0

def main():
    parser = argparse.ArgumentParser(description='Migrate files between storage providers')
    parser.add_argument(
        '--source',
        type=str,
        choices=['b2', 's3'],
        help='Source storage provider'
    )
    parser.add_argument(
        '--target',
        type=str,
        choices=['b2', 's3'],
        help='Target storage provider'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Number of files to process in each batch'
    )
    
    args = parser.parse_args()
    
    # If source/target not provided, use current and desired providers
    source = args.source or settings.STORAGE_PROVIDER
    target = args.target
    
    if not target:
        logger.error("Target storage provider must be specified")
        return
    
    if source == target:
        logger.error("Source and target providers must be different")
        return
    
    success = asyncio.run(migrate_storage(source, target, args.batch_size))
    
    if success:
        logger.info("\nMigration completed successfully!")
    else:
        logger.error("\nMigration completed with errors. Please check the logs.")

if __name__ == "__main__":
    main() 