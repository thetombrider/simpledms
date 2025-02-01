from typing import List, Optional
from fastapi import APIRouter, File, Form, UploadFile, Query, HTTPException
from datetime import datetime
from pydantic import BaseModel
from ....models.document import Document
from ....services.b2 import B2Service

router = APIRouter()
b2_service = B2Service()

@router.get("/")
async def list_documents(
    owner_id: str,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    category: Optional[str] = None,
    tag: Optional[str] = None
) -> List[Document]:
    """List documents with optional filtering"""
    query = {"owner_id": owner_id}
    if category:
        query["categories"] = category
    if tag:
        query["tags"] = tag
    
    return await Document.find(query).skip(skip).limit(limit).to_list()

@router.post("/")
async def create_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    categories: List[str] = Form([]),  # Accept as list directly
    tags: List[str] = Form([]),  # Accept as list directly
    owner_id: str = Form(...)
) -> Document:
    """Create a new document"""
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)
    
    # Generate S3 key (path in B2)
    current_time = datetime.utcnow()
    file_path = f"documents/{owner_id}/{current_time.year}/{current_time.month:02d}/{current_time.day:02d}/{file.filename}"
    
    # Create document metadata
    document = Document(
        title=title,
        description=description,
        file_name=file.filename,
        file_size=file_size,
        mime_type=file.content_type or "application/octet-stream",
        s3_key=file_path,
        categories=categories,
        tags=tags,
        owner_id=owner_id
    )
    
    # Upload file to B2
    await b2_service.upload_file(file_content, file_path)
    
    # Save document metadata
    await document.insert()
    return document

@router.get("/{document_id}/download")
async def get_download_url(document_id: str, owner_id: str) -> dict:
    """Get download URL for a document"""
    document = await Document.get(document_id)
    if not document or document.owner_id != owner_id:
        raise HTTPException(status_code=404, detail="Document not found")
    
    url = await b2_service.generate_download_url(document.s3_key)
    return {"download_url": url}

@router.delete("/{document_id}")
async def delete_document(document_id: str, owner_id: str):
    """Delete a document"""
    document = await Document.get(document_id)
    if not document or document.owner_id != owner_id:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete from B2
    await b2_service.delete_file(document.s3_key)
    
    # Delete metadata
    await document.delete()
    return {"status": "success"} 