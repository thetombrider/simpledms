from typing import List
from fastapi import APIRouter, HTTPException
from ....models.category import Category
from ....models.tag import Tag

router = APIRouter()

@router.get("/categories/", response_model=List[Category])
async def list_categories():
    """Get all categories"""
    return await Category.find_all().to_list()

@router.post("/categories/", response_model=Category)
async def create_category(category: Category):
    """Create a new category"""
    try:
        return await category.insert()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Category creation failed: {str(e)}")

@router.delete("/categories/{name}")
async def delete_category(name: str):
    """Delete a category"""
    category = await Category.find_one({"name": name})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await category.delete()
    return {"status": "success"}

@router.get("/tags/", response_model=List[Tag])
async def list_tags():
    """Get all tags"""
    return await Tag.find_all().to_list()

@router.post("/tags/", response_model=Tag)
async def create_tag(tag: Tag):
    """Create a new tag"""
    try:
        return await tag.insert()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Tag creation failed: {str(e)}")

@router.delete("/tags/{name}")
async def delete_tag(name: str):
    """Delete a tag"""
    tag = await Tag.find_one({"name": name})
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    await tag.delete()
    return {"status": "success"} 