from fastapi import APIRouter, HTTPException
from typing import List
from app.models.category import Category
from app.services.config import ConfigService

router = APIRouter()
config_service = ConfigService()

@router.get("/", response_model=List[Category])
async def get_categories():
    """Get all categories"""
    try:
        return await config_service.get_categories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Category)
async def create_category(category: Category):
    """Create a new category"""
    try:
        return await config_service.create_category(category)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{name}")
async def delete_category(name: str):
    """Delete a category"""
    try:
        await config_service.delete_category(name)
        return {"message": f"Category {name} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) 