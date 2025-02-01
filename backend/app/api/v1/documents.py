from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from ...services.document import DocumentService
from ...models.document import Document

router = APIRouter()
document_service = DocumentService()

@router.post("/", response_model=Document)
async def create_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    categories: List[str] = Form([]),
    tags: List[str] = Form([]),
    owner_id: str = "test_user"  # TODO: Get from auth
):
    """Upload a new document"""
    return await document_service.create_document(
        file=file,
        title=title,
        description=description,
        categories=categories,
        tags=tags,
        owner_id=owner_id
    )

@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: str,
    owner_id: str = "test_user"  # TODO: Get from auth
):
    """Get document metadata"""
    return await document_service.get_document(document_id, owner_id)

@router.get("/", response_model=List[Document])
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    tag: Optional[str] = None,
    owner_id: str = "test_user"  # TODO: Get from auth
):
    """List documents with optional filtering"""
    return await document_service.list_documents(
        owner_id=owner_id,
        skip=skip,
        limit=limit,
        category=category,
        tag=tag
    )

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    owner_id: str = "test_user"  # TODO: Get from auth
):
    """Delete a document"""
    await document_service.delete_document(document_id, owner_id)
    return {"message": "Document deleted successfully"}

@router.get("/{document_id}/download")
async def get_download_url(
    document_id: str,
    owner_id: str = "test_user"  # TODO: Get from auth
):
    """Get a presigned download URL for a document"""
    url = await document_service.generate_download_url(document_id, owner_id)
    return {"download_url": url}

@router.patch("/{document_id}", response_model=Document)
async def update_document(
    document_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    categories: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    owner_id: str = "test_user"  # TODO: Get from auth
):
    """Update document metadata"""
    return await document_service.update_document(
        document_id=document_id,
        owner_id=owner_id,
        title=title,
        description=description,
        categories=categories,
        tags=tags
    ) 