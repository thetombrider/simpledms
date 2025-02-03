from typing import List, Optional
from fastapi import UploadFile, HTTPException
import mimetypes
from datetime import datetime

from ..models.document import Document
from .storage.factory import get_storage_provider

class DocumentService:
    def __init__(self):
        self.storage = get_storage_provider()

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
            s3_key=file_path,
            categories=categories,
            tags=tags,
            owner_id=owner_id
        )
        
        try:
            # Upload file to storage first
            await self.storage.upload_file(file_content, file_path)
            
            try:
                # Then save document metadata
                await document.insert()
                return document
            except Exception as e:
                # If MongoDB insert fails, clean up storage
                try:
                    await self.storage.delete_file(file_path)
                except:
                    pass  # Best effort cleanup
                raise e
                
        except Exception as e:
            # Storage upload failed, don't create MongoDB document
            raise HTTPException(
                status_code=500,
                detail=f"Error uploading file: {str(e)}"
            )

    async def get_document(self, document_id: str, owner_id: str) -> Document:
        """Get a document by ID"""
        document = await Document.get(document_id)
        if not document or document.owner_id != owner_id:
            raise HTTPException(status_code=404, detail="Document not found")
        
        try:
            # Verify file exists in storage
            await self.storage.get_file_info(document.s3_key)
        except HTTPException as e:
            if e.status_code == 404:
                # File doesn't exist in storage, clean up orphaned metadata
                await document.delete()
                raise HTTPException(
                    status_code=404,
                    detail="Document not found in storage. Metadata has been cleaned up."
                )
            raise
        
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
            
        documents = await query.to_list()
        valid_documents = []
        
        # Check each document's file existence and clean up orphaned ones
        for doc in documents:
            try:
                await self.storage.get_file_info(doc.s3_key)
                valid_documents.append(doc)
            except HTTPException as e:
                if e.status_code == 404:
                    # File doesn't exist in storage, delete the orphaned metadata
                    await doc.delete()
                else:
                    # For other errors, keep the document in the list
                    valid_documents.append(doc)
        
        # Apply skip and limit after filtering
        start = min(skip, len(valid_documents))
        end = min(start + limit, len(valid_documents))
        return valid_documents[start:end]

    async def delete_document(self, document_id: str, owner_id: str) -> None:
        """Delete a document"""
        document = await self.get_document(document_id, owner_id)
        
        try:
            # Delete from storage first
            await self.storage.delete_file(document.s3_key)
        except HTTPException as e:
            if e.status_code != 404:  # Ignore if already deleted
                raise
        
        # Then delete metadata
        await document.delete()

    async def generate_download_url(self, document_id: str, owner_id: str) -> str:
        """Generate a download URL for a document"""
        document = await self.get_document(document_id, owner_id)
        return await self.storage.generate_download_url(document.s3_key)

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

    async def cleanup_orphaned_documents(self) -> int:
        """Clean up documents where storage file is missing"""
        cleaned = 0
        async for doc in Document.find_all():
            try:
                await self.storage.get_file_info(doc.s3_key)
            except HTTPException as e:
                if e.status_code == 404:
                    await doc.delete()
                    cleaned += 1
        return cleaned 