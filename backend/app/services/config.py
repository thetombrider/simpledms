from typing import List
from app.models.category import Category
from app.models.tag import Tag

class ConfigService:
    async def get_categories(self) -> List[Category]:
        """Get all categories"""
        return await Category.find_all().to_list()

    async def create_category(self, category: Category) -> Category:
        """Create a new category"""
        return await category.create()

    async def delete_category(self, name: str):
        """Delete a category"""
        category = await Category.find_one(Category.name == name)
        if not category:
            raise ValueError(f"Category {name} not found")
        await category.delete()

    async def get_tags(self) -> List[Tag]:
        """Get all tags"""
        return await Tag.find_all().to_list()

    async def create_tag(self, tag: Tag) -> Tag:
        """Create a new tag"""
        return await tag.create()

    async def delete_tag(self, name: str):
        """Delete a tag"""
        tag = await Tag.find_one(Tag.name == name)
        if not tag:
            raise ValueError(f"Tag {name} not found")
        await tag.delete() 