import streamlit as st
import httpx
import json
import asyncio
from typing import Optional, List, Dict
from datetime import datetime

# Constants
API_URL = "http://localhost:8080/api/v1"  # Updated port to match backend
TEMP_USER_ID = "test_user"  # We'll replace this with real auth later

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
            st.error(f"Upload error details: {str(e)}")
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

# Initialize API client
api = DocumentAPI(API_URL)

# Helper function to run async operations
def run_async_operation(func, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(func(*args, **kwargs))
        return result
    except Exception as e:
        raise e
    finally:
        loop.close()
        asyncio.set_event_loop(None)

# Set page config
st.set_page_config(
    page_title="SimpleS3DMS",
    page_icon="📄",
    layout="wide"
)

# Title
st.title("📄 SimpleS3DMS")
st.subheader("Simple Document Management System")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to", ["Upload", "Documents"])

# Main content
if page == "Upload":
    st.header("Upload Document")
    
    with st.form("upload_form"):
        uploaded_file = st.file_uploader("Choose a file", type=None)
        title = st.text_input("Title")
        description = st.text_area("Description")
        categories = st.multiselect(
            "Categories",
            ["Invoice", "Contract", "Report", "Other"],
            default=[]
        )
        tags = st.text_input("Tags (comma-separated)").split(",")
        tags = [tag.strip() for tag in tags if tag.strip()]
        
        submit = st.form_submit_button("Upload")
        
        if submit and uploaded_file is not None:
            if not title:
                st.error("Please provide a title")
            else:
                with st.spinner("Uploading document..."):
                    try:
                        document = run_async_operation(
                            api.upload_document,
                            uploaded_file,
                            title,
                            description,
                            categories,
                            tags,
                            TEMP_USER_ID
                        )
                        st.success("Document uploaded successfully!")
                        st.json(document)
                    except Exception as e:
                        st.error(f"Error uploading document: {str(e)}")

else:  # Documents page
    st.header("My Documents")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        filter_category = st.selectbox(
            "Filter by category",
            ["All"] + ["Invoice", "Contract", "Report", "Other"]
        )
    with col2:
        filter_tag = st.text_input("Filter by tag")
    
    # List documents
    try:
        documents = run_async_operation(
            api.list_documents,
            owner_id=TEMP_USER_ID,
            category=None if filter_category == "All" else filter_category,
            tag=filter_tag if filter_tag else None
        )
        
        if not documents:
            st.info("No documents found")
        else:
            for doc in documents:
                with st.expander(f"{doc['title']} ({doc['file_name']})"):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"Description: {doc['description']}")
                        st.write(f"Categories: {', '.join(doc['categories'])}")
                        st.write(f"Tags: {', '.join(doc['tags'])}")
                        st.write(f"Size: {doc['file_size']} bytes")
                        st.write(f"Uploaded: {doc['created_at']}")
                    
                    with col2:
                        if st.button("Download", key=f"download_{doc['_id']}"):
                            with st.spinner("Generating download link..."):
                                try:
                                    url = run_async_operation(
                                        api.get_download_url,
                                        doc['_id'],
                                        TEMP_USER_ID
                                    )
                                    st.markdown(f"[Click here to download]({url})")
                                except Exception as e:
                                    st.error(f"Error generating download link: {str(e)}")
                    
                    with col3:
                        delete_key = f"delete_{doc['_id']}"
                        
                        # Initialize session state for this document if not exists
                        if f"delete_confirm_{doc['_id']}" not in st.session_state:
                            st.session_state[f"delete_confirm_{doc['_id']}"] = False
                        
                        # Show confirmation dialog
                        if st.session_state[f"delete_confirm_{doc['_id']}"]:
                            st.warning(f"Are you sure you want to delete {doc['title']}?")
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("Yes", key=f"yes_{doc['_id']}"):
                                    with st.spinner("Deleting document..."):
                                        try:
                                            run_async_operation(
                                                api.delete_document,
                                                doc['_id'],
                                                TEMP_USER_ID
                                            )
                                            st.success("Document deleted successfully!")
                                            # Reset confirmation state
                                            st.session_state[f"delete_confirm_{doc['_id']}"] = False
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Error deleting document: {str(e)}")
                            with col2:
                                if st.button("No", key=f"no_{doc['_id']}"):
                                    # Reset confirmation state
                                    st.session_state[f"delete_confirm_{doc['_id']}"] = False
                                    st.rerun()
                        else:
                            if st.button("Delete", key=delete_key):
                                # Set confirmation state
                                st.session_state[f"delete_confirm_{doc['_id']}"] = True
                                st.rerun()
    
    except Exception as e:
        st.error(f"Error loading documents: {str(e)}") 