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
            s3_key=file_path,
            categories=categories,
            tags=tags,
            owner_id=owner_id
        )
        
        try:
            # Upload file to B2 first
            await self.b2_service.upload_file(file_content, file_path)
            
            try:
                # Then save document metadata
                await document.insert()
                return document
            except Exception as e:
                # If MongoDB insert fails, clean up B2
                try:
                    await self.b2_service.delete_file(file_path)
                except:
                    pass  # Best effort cleanup
                raise e
                
        except Exception as e:
            # B2 upload failed, don't create MongoDB document
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
            # Verify file exists in B2
            await self.b2_service.get_file_info(document.s3_key)
        except HTTPException as e:
            if e.status_code == 404:
                # File doesn't exist in B2, clean up orphaned metadata
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
                await self.b2_service.get_file_info(doc.s3_key)
                valid_documents.append(doc)
            except HTTPException as e:
                if e.status_code == 404:
                    # File doesn't exist in B2, delete the orphaned metadata
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
            # Delete from B2 first
            await self.b2_service.delete_file(document.s3_key)
        except HTTPException as e:
            if e.status_code != 404:  # Ignore if already deleted
                raise
        
        # Then delete metadata
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

    async def cleanup_orphaned_documents(self) -> int:
        """Clean up documents where B2 file is missing"""
        cleaned = 0
        async for doc in Document.find_all():
            try:
                await self.b2_service.get_file_info(doc.s3_key)
            except HTTPException as e:
                if e.status_code == 404:
                    await doc.delete()
                    cleaned += 1
        return cleaned 