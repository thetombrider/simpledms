from typing import List, Optional
from fastapi import UploadFile, HTTPException
import mimetypes
from datetime import datetime

from ..models.document import Document
from .b2 import B2Service

class DocumentService:
    def __init__(self):
        self.b2_service = B2Service()

    async def create_document(
        self,
        file: UploadFile,
        title: str,
        description: Optional[str],
        categories: List[str],
        tags: List[str],
        owner_id: str
    ) -> Document:
        """Create a new document"""
        
        # Generate file path
        timestamp = datetime.utcnow().strftime("%Y/%m/%d")
        file_path = f"documents/{owner_id}/{timestamp}/{file.filename}"
        
        # Guess mime type
        mime_type, _ = mimetypes.guess_type(file.filename)
        if not mime_type:
            mime_type = "application/octet-stream"
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Create document metadata
        document = Document(
            title=title,
            description=description,
            file_name=file.filename,
            file_size=file_size,
            mime_type=mime_type,
            s3_key=file_path,  # We'll keep the field name as s3_key for compatibility
            categories=categories,
            tags=tags,
            owner_id=owner_id
        )
        
        # Upload file to B2
        await self.b2_service.upload_file(file_content, file_path)
        
        # Save document metadata
        await document.insert()
        
        return document

    async def get_document(self, document_id: str, owner_id: str) -> Document:
        """Get a document by ID"""
        document = await Document.get(document_id)
        if not document or document.owner_id != owner_id:
            raise HTTPException(status_code=404, detail="Document not found")
        return document

    async def list_documents(
        self,
        owner_id: str,
        skip: int = 0,
        limit: int = 10,
        category: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[Document]:
        """List documents with optional filtering"""
        query = Document.find(Document.owner_id == owner_id)
        
        if category:
            query = query.find(Document.categories == category)
        if tag:
            query = query.find(Document.tags == tag)
            
        documents = await query.skip(skip).limit(limit).to_list()
        return documents

    async def delete_document(self, document_id: str, owner_id: str) -> None:
        """Delete a document"""
        document = await self.get_document(document_id, owner_id)
        
        # Delete from B2
        await self.b2_service.delete_file(document.s3_key)
        
        # Delete metadata
        await document.delete()

    async def generate_download_url(self, document_id: str, owner_id: str) -> str:
        """Generate a download URL for a document"""
        document = await self.get_document(document_id, owner_id)
        return await self.b2_service.generate_download_url(document.s3_key)

    async def update_document(
        self,
        document_id: str,
        owner_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> Document:
        """Update document metadata"""
        document = await self.get_document(document_id, owner_id)
        
        if title is not None:
            document.title = title
        if description is not None:
            document.description = description
        if categories is not None:
            document.categories = categories
        if tags is not None:
            document.tags = tags
            
        await document.save()
        return document 