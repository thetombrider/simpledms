# Storage Abstraction Layer Documentation

## Overview

The storage abstraction layer provides a unified interface for storing and retrieving files across different storage providers. Currently supported providers:
- Backblaze B2
- Amazon S3

## Configuration

### Environment Variables

Configure your storage provider in `.env`:

```env
# Storage Provider settings
STORAGE_PROVIDER=b2  # Options: b2 or s3

# B2 settings (if using B2)
B2_KEY_ID=your_b2_key_id
B2_APPLICATION_KEY=your_b2_application_key
B2_BUCKET_NAME=your_b2_bucket_name

# AWS S3 settings (if using S3)
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=your_aws_region
S3_BUCKET_NAME=your_s3_bucket_name
```

### Provider-Specific Setup

#### Backblaze B2
1. Create a B2 account at https://www.backblaze.com/b2/sign-up.html
2. Create a bucket and application key with:
   - Read and Write permissions
   - File list permissions
   - Bucket creation permissions
3. Copy the key ID and application key to your `.env` file

#### Amazon S3
1. Create an AWS account
2. Create an S3 bucket
3. Create an IAM user with the following permissions:
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "s3:PutObject",
                   "s3:GetObject",
                   "s3:DeleteObject",
                   "s3:ListBucket"
               ],
               "Resource": [
                   "arn:aws:s3:::your-bucket-name",
                   "arn:aws:s3:::your-bucket-name/*"
               ]
           }
       ]
   }
   ```
4. Copy the access key ID and secret access key to your `.env` file

## Usage

### Basic Usage

The storage provider is automatically initialized based on your configuration:

```python
from app.services.storage.factory import get_storage_provider

# Get configured storage provider
storage = get_storage_provider()

# Upload a file
file_path = await storage.upload_file(file_content, "path/to/file.txt")

# Download a file
file_data = await storage.download_file("path/to/file.txt")

# Generate a download URL
url = await storage.generate_download_url("path/to/file.txt", duration_in_seconds=3600)

# Delete a file
await storage.delete_file("path/to/file.txt")

# Get file info
info = await storage.get_file_info("path/to/file.txt")
```

### Storage Provider Interface

All storage providers implement the following interface:

```python
class StorageProvider(ABC):
    @abstractmethod
    async def upload_file(self, file: Union[BinaryIO, bytes], file_path: str) -> str:
        """Upload a file and return its path/id"""
        pass
    
    @abstractmethod
    async def download_file(self, file_path: str) -> BinaryIO:
        """Download a file"""
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> None:
        """Delete a file"""
        pass
    
    @abstractmethod
    async def generate_download_url(self, file_path: str, duration_in_seconds: int = 3600) -> str:
        """Generate a download URL"""
        pass
    
    @abstractmethod
    async def get_file_info(self, file_path: str) -> Dict:
        """Get file metadata"""
        pass
```

## Migration Between Providers

### Using the Migration Script

To migrate files between storage providers:

```bash
# Migrate from B2 to S3
python backend/migrate_storage.py --target s3

# Migrate from S3 to B2
python backend/migrate_storage.py --target b2

# Customize batch size
python backend/migrate_storage.py --target s3 --batch-size 20
```

### Migration Process

1. Files are migrated in batches to prevent memory issues
2. Each file is:
   - Downloaded from the source provider
   - Uploaded to the target provider
   - Verified after upload
3. Failed migrations are logged and can be retried
4. A verification step ensures all files were migrated correctly

### Migration Results

The migration script provides detailed results:
- Total files processed
- Successfully migrated files
- Failed migrations
- List of failed files
- Verification results

Example output:
```
Starting migration from b2 to s3
Migrating files...
Migration completed:
Total files: 100
Successfully migrated: 98
Failed: 2

Failed files:
  - documents/user1/2024/03/01/failed1.pdf
  - documents/user2/2024/03/01/failed2.jpg

Verifying migration...
Verification completed:
Total files: 100
Verified: 98
Missing: 2
```

## Error Handling

The storage abstraction layer provides consistent error handling across providers:

- `HTTPException(404)`: File not found
- `HTTPException(500)`: General storage error
- Provider-specific errors are wrapped in appropriate HTTP exceptions

## Best Practices

1. **File Paths**
   - Use consistent path formatting: `documents/{user_id}/{year}/{month}/{day}/{filename}`
   - Avoid special characters in file paths
   - Use forward slashes (/) for path separation

2. **Error Handling**
   - Always handle potential storage errors
   - Implement cleanup in case of partial failures
   - Verify file existence before operations

3. **Performance**
   - Use batch operations when possible
   - Generate download URLs instead of streaming large files
   - Implement appropriate timeouts

4. **Security**
   - Never expose storage credentials
   - Use temporary download URLs
   - Implement proper access controls

## Extending the Storage Layer

To add a new storage provider:

1. Create a new provider class implementing `StorageProvider`
2. Add provider configuration to `Settings` class
3. Update `StorageFactory` to support the new provider
4. Add migration support in `StorageMigration`
5. Update documentation and tests 