from fastapi import APIRouter, HTTPException
from typing import List
from app.models.tag import Tag
from app.services.config import ConfigService

router = APIRouter()
config_service = ConfigService()

@router.get("/", response_model=List[Tag])
async def get_tags():
    """Get all tags"""
    try:
        return await config_service.get_tags()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Tag)
async def create_tag(tag: Tag):
    """Create a new tag"""
    try:
        return await config_service.create_tag(tag)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{name}")
async def delete_tag(name: str):
    """Delete a tag"""
    try:
        await config_service.delete_tag(name)
        return {"message": f"Tag {name} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) 