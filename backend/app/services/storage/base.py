from abc import ABC, abstractmethod
from typing import BinaryIO, Optional, Dict, Union

class StorageProvider(ABC):
    """Abstract base class for storage providers"""
    
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
