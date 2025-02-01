import httpx
from typing import Optional, List, Dict
from datetime import datetime

class DocumentAPI:
    """API client for interacting with the backend"""
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    async def _get_client(self):
        return httpx.AsyncClient(timeout=30.0)
    
    async def upload_document(
        self,
        file,
        title: str,
        description: Optional[str],
        categories: List[str],
        tags: List[str],
        owner_id: str
    ) -> Dict:
        """Upload a document to the backend"""
        try:
            url = f"{self.base_url}/documents/"
            
            # Get file size and mime type
            file_content = file.read()
            file_size = len(file_content)
            mime_type = file.type or "application/octet-stream"
            file.seek(0)  # Reset file pointer
            
            # Prepare form data
            form_data = {
                "title": title,
                "description": description or "",
                "categories": categories,
                "tags": tags,
                "owner_id": owner_id,
                "file_name": file.name,
                "file_size": str(file_size),
                "mime_type": mime_type
            }
            
            # Create a new client for this request
            async with await self._get_client() as client:
                response = await client.post(
                    url,
                    files={"file": file},
                    data=form_data,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            
        except Exception as e:
            raise
    
    async def list_documents(
        self,
        owner_id: str,
        skip: int = 0,
        limit: int = 10,
        category: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[Dict]:
        """List documents from the backend"""
        params = {
            "owner_id": owner_id,
            "skip": skip,
            "limit": limit
        }
        if category:
            params["category"] = category
        if tag:
            params["tag"] = tag
        
        async with await self._get_client() as client:
            response = await client.get(f"{self.base_url}/documents/", params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_download_url(self, document_id: str, owner_id: str) -> str:
        """Get download URL for a document"""
        async with await self._get_client() as client:
            response = await client.get(
                f"{self.base_url}/documents/{document_id}/download",
                params={"owner_id": owner_id}
            )
            response.raise_for_status()
            return response.json()["download_url"]
    
    async def delete_document(self, document_id: str, owner_id: str) -> None:
        """Delete a document"""
        async with await self._get_client() as client:
            response = await client.delete(
                f"{self.base_url}/documents/{document_id}",
                params={"owner_id": owner_id}
            )
            response.raise_for_status()
    
    async def list_categories(self) -> List[Dict]:
        """Get all available categories"""
        async with await self._get_client() as client:
            response = await client.get(f"{self.base_url}/config/categories/")
            response.raise_for_status()
            return response.json()
    
    async def create_category(self, name: str, icon: str, description: Optional[str] = None) -> Dict:
        """Create a new category"""
        async with await self._get_client() as client:
            response = await client.post(
                f"{self.base_url}/config/categories/",
                json={"name": name, "icon": icon, "description": description}
            )
            response.raise_for_status()
            return response.json()
    
    async def delete_category(self, name: str) -> None:
        """Delete a category"""
        async with await self._get_client() as client:
            response = await client.delete(f"{self.base_url}/config/categories/{name}")
            response.raise_for_status()
    
    async def list_tags(self) -> List[Dict]:
        """Get all available tags"""
        async with await self._get_client() as client:
            response = await client.get(f"{self.base_url}/config/tags/")
            response.raise_for_status()
            return response.json()
    
    async def create_tag(self, name: str, color: str) -> Dict:
        """Create a new tag"""
        async with await self._get_client() as client:
            response = await client.post(
                f"{self.base_url}/config/tags/",
                json={"name": name, "color": color}
            )
            response.raise_for_status()
            return response.json()
    
    async def delete_tag(self, name: str) -> None:
        """Delete a tag"""
        async with await self._get_client() as client:
            response = await client.delete(f"{self.base_url}/config/tags/{name}")
            response.raise_for_status()
    
    async def get_user_stats(self, owner_id: str) -> Dict:
        """Get statistics about user's documents"""
        async with await self._get_client() as client:
            # Get documents in batches of 100
            all_documents = []
            skip = 0
            while True:
                response = await client.get(
                    f"{self.base_url}/documents/",
                    params={
                        "owner_id": owner_id,
                        "skip": skip,
                        "limit": 100
                    }
                )
                response.raise_for_status()
                batch = response.json()
                all_documents.extend(batch)
                
                if len(batch) < 100:  # Less than 100 documents returned means we've got all
                    break
                skip += 100
            
            # Calculate statistics
            total_docs = len(all_documents)
            total_size = sum(doc['file_size'] for doc in all_documents)
            categories_count = {}
            tags_count = {}
            docs_by_month = {}
            
            for doc in all_documents:
                # Count categories
                for cat in doc['categories']:
                    categories_count[cat] = categories_count.get(cat, 0) + 1
                
                # Count tags
                for tag in doc['tags']:
                    tags_count[tag] = tags_count.get(tag, 0) + 1
                
                # Group by month
                created_at = datetime.fromisoformat(doc['created_at'].replace('Z', '+00:00'))
                month_key = created_at.strftime('%Y-%m')
                docs_by_month[month_key] = docs_by_month.get(month_key, 0) + 1
            
            return {
                "total_documents": total_docs,
                "total_size": total_size,
                "categories_distribution": categories_count,
                "tags_distribution": tags_count,
                "documents_by_month": dict(sorted(docs_by_month.items())),
                "most_used_category": max(categories_count.items(), key=lambda x: x[1])[0] if categories_count else None,
                "most_used_tag": max(tags_count.items(), key=lambda x: x[1])[0] if tags_count else None
            } 