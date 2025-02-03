# Storage Provider Implementation Guide

This guide explains how to implement a new storage provider for SimpleS3DMS.

## Overview

The storage abstraction layer is designed to be extensible. Each storage provider must implement the `StorageProvider` abstract base class, which defines the common interface for all storage operations.

## Implementation Steps

### 1. Create Provider Class

Create a new file in the `storage` directory (e.g., `my_provider.py`):

```python
from typing import BinaryIO, Optional, Dict, Union
from fastapi import HTTPException
from .base import StorageProvider

class MyStorageProvider(StorageProvider):
    def __init__(self, config_param1: str, config_param2: str):
        # Initialize your storage client/connection here
        self.client = MyStorageClient(config_param1, config_param2)
```

### 2. Implement Required Methods

Your provider must implement all abstract methods from `StorageProvider`:

```python
async def upload_file(self, file: Union[BinaryIO, bytes], file_path: str) -> str:
    """
    Upload a file to storage.
    
    Args:
        file: File content as bytes or file-like object
        file_path: Destination path in storage
        
    Returns:
        str: The path/id of the uploaded file
        
    Raises:
        HTTPException: On upload failure
    """
    try:
        # Implement file upload
        return file_path
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

async def download_file(self, file_path: str) -> BinaryIO:
    """
    Download a file from storage.
    
    Args:
        file_path: Path of file to download
        
    Returns:
        BinaryIO: File content as a file-like object
        
    Raises:
        HTTPException: If file not found or download fails
    """
    try:
        # Implement file download
        pass
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Download failed: {str(e)}"
        )

async def delete_file(self, file_path: str) -> None:
    """
    Delete a file from storage.
    
    Args:
        file_path: Path of file to delete
        
    Raises:
        HTTPException: If deletion fails
    """
    try:
        # Implement file deletion
        pass
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Deletion failed: {str(e)}"
        )

async def generate_download_url(
    self,
    file_path: str,
    duration_in_seconds: int = 3600
) -> str:
    """
    Generate a temporary download URL.
    
    Args:
        file_path: Path of file to generate URL for
        duration_in_seconds: URL validity duration
        
    Returns:
        str: Temporary download URL
        
    Raises:
        HTTPException: If URL generation fails
    """
    try:
        # Implement URL generation
        pass
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"URL generation failed: {str(e)}"
        )

async def get_file_info(self, file_path: str) -> Dict:
    """
    Get file metadata.
    
    Args:
        file_path: Path of file to get info for
        
    Returns:
        Dict: File metadata including:
            - file_name: str
            - content_type: str
            - content_length: int
            - upload_timestamp: datetime
            
    Raises:
        HTTPException: If file not found or info retrieval fails
    """
    try:
        # Implement metadata retrieval
        pass
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Info retrieval failed: {str(e)}"
        )
```

### 3. Add Configuration

Update `config.py` to include your provider's settings:

```python
class Settings(BaseSettings):
    # Existing settings...
    
    # Your provider settings
    MY_PROVIDER_SETTING1: Optional[str] = None
    MY_PROVIDER_SETTING2: Optional[str] = None
    
    def validate_storage_config(self):
        if self.STORAGE_PROVIDER == "my_provider":
            if not all([
                self.MY_PROVIDER_SETTING1,
                self.MY_PROVIDER_SETTING2
            ]):
                raise ValueError(
                    "my_provider requires SETTING1 and SETTING2"
                )
```

### 4. Update Factory

Add your provider to `factory.py`:

```python
from .my_provider import MyStorageProvider

class StorageFactory:
    @staticmethod
    def get_provider(
        provider_type: str,
        settings: Optional[dict] = None
    ) -> StorageProvider:
        # Existing providers...
        
        elif provider_type == "my_provider":
            return MyStorageProvider(
                config_param1=settings.get('setting1')
                    or settings.MY_PROVIDER_SETTING1,
                config_param2=settings.get('setting2')
                    or settings.MY_PROVIDER_SETTING2
            )
```

## Best Practices

1. **Error Handling**
   - Use appropriate HTTP status codes
   - Wrap provider-specific errors in HTTPException
   - Include helpful error messages

2. **File Operations**
   - Support both bytes and file-like objects for uploads
   - Always return file-like objects for downloads
   - Implement proper cleanup in error cases

3. **Performance**
   - Use async operations where possible
   - Implement efficient batch operations
   - Handle large files appropriately

4. **Testing**
   - Write unit tests for your provider
   - Test with various file types and sizes
   - Test error conditions

## Example Implementation

See `b2.py` and `s3.py` for complete examples of storage provider implementations.

## Testing Your Provider

1. Create a test file similar to `test_storage.py`
2. Test all basic operations:
   - Upload
   - Download
   - Delete
   - URL generation
   - Metadata retrieval
3. Test error conditions
4. Test with the migration utility

## Common Pitfalls

1. **Memory Management**
   - Don't load entire files into memory
   - Use streaming where possible
   - Clean up temporary files

2. **Error Handling**
   - Don't expose internal errors to users
   - Handle connection timeouts
   - Implement proper retries

3. **Configuration**
   - Validate all required settings
   - Use appropriate defaults
   - Document all configuration options 