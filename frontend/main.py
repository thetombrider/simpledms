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

# Initialize API client
api = DocumentAPI(API_URL)

# Cache for categories
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_categories():
    """Get list of category names from the database"""
    try:
        categories = run_async_operation(api.list_categories)
        if not categories:  # If no categories in DB, use defaults
            return ["Invoice", "Contract", "Report", "Other"]
        return [cat["name"] for cat in categories]
    except Exception as e:
        st.error(f"Error loading categories: {str(e)}")
        return ["Invoice", "Contract", "Report", "Other"]  # Fallback only on error

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

def show_upload_page():
    """Upload page content"""
    st.header("Upload Document")
    
    with st.form("upload_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_file = st.file_uploader("Choose a file", type=None)
            title = st.text_input("Title")
            description = st.text_area("Description")
        
        with col2:
            categories = st.multiselect(
                "Categories",
                options=get_categories(),
                default=[]
            )
            tags_input = st.text_input("Tags (comma-separated)")
            tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
        
        submit_button = st.form_submit_button("Upload Document", use_container_width=True)
        
        if submit_button:
            if not uploaded_file:
                st.error("Please select a file to upload")
            elif not title:
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

def show_documents_page():
    """Documents page content"""
    st.header("My Documents")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        filter_category = st.selectbox(
            "Filter by category",
            ["All"] + get_categories()
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

def show_config_page():
    """Configuration page content"""
    st.header("Configuration")
    
    # Initialize session state for form submission tracking
    if 'category_submitted' not in st.session_state:
        st.session_state.category_submitted = False
    if 'tag_submitted' not in st.session_state:
        st.session_state.tag_submitted = False

    # Categories Section
    st.subheader("Categories")
    
    # Category form
    with st.form("category_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_category_name = st.text_input("Category Name")
            new_category_description = st.text_area("Description (optional)")
        with col2:
            new_category_icon = st.text_input("Icon", value="📄")
        
        submit_category = st.form_submit_button("Add Category", use_container_width=True)
        
        if submit_category and new_category_name:
            try:
                run_async_operation(
                    lambda: api.create_category(
                        name=new_category_name,
                        icon=new_category_icon,
                        description=new_category_description if new_category_description else None
                    )
                )
                st.success(f"Category '{new_category_name}' added successfully!")
                st.session_state.category_submitted = True
                st.rerun()
            except Exception as e:
                st.error(f"Error adding category: {str(e)}")
    
    # Display existing categories
    try:
        categories = run_async_operation(api.list_categories)
        if categories:
            st.subheader("Existing Categories")
            for cat in categories:
                with st.container():
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col1:
                        st.write(cat["icon"])
                    with col2:
                        st.write(cat["name"])
                        if cat.get("description"):
                            st.caption(cat["description"])
                    with col3:
                        if st.button("Delete", key=f"del_cat_{cat['name']}", use_container_width=True):
                            try:
                                run_async_operation(
                                    lambda: api.delete_category(cat['name'])
                                )
                                st.success(f"Category '{cat['name']}' deleted successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting category: {str(e)}")
    except Exception as e:
        st.error(f"Error loading categories: {str(e)}")

    # Tags Section
    st.subheader("Tags")
    
    # Tag form
    with st.form("tag_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_tag_name = st.text_input("Tag Name")
        with col2:
            new_tag_color = st.color_picker("Color", value="#808080")
        
        submit_tag = st.form_submit_button("Add Tag", use_container_width=True)
        
        if submit_tag and new_tag_name:
            try:
                run_async_operation(
                    lambda: api.create_tag(new_tag_name, new_tag_color)
                )
                st.success(f"Tag '{new_tag_name}' added successfully!")
                st.session_state.tag_submitted = True
                st.rerun()
            except Exception as e:
                st.error(f"Error adding tag: {str(e)}")
    
    # Display existing tags
    try:
        tags = run_async_operation(api.list_tags)
        if tags:
            st.subheader("Existing Tags")
            for tag in tags:
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.markdown(f"<div style='width: 20px; height: 20px; background-color: {tag['color']}; border-radius: 50%;'></div>", unsafe_allow_html=True)
                with col2:
                    st.write(tag["name"])
                with col3:
                    if st.button("Delete", key=f"del_tag_{tag['name']}", use_container_width=True):
                        try:
                            run_async_operation(
                                lambda: api.delete_tag(tag['name'])
                            )
                            st.success(f"Tag '{tag['name']}' deleted successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting tag: {str(e)}")
    except Exception as e:
        st.error(f"Error loading tags: {str(e)}")

# Set page config
st.set_page_config(
    page_title="SimpleS3DMS",
    page_icon="📄",
    layout="wide"
)

# Title
st.title("📄 SimpleS3DMS")
st.subheader("Simple Document Management System")

# Initialize page in session state if not exists
if "page" not in st.session_state:
    st.session_state.page = "upload"

# Sidebar Navigation
with st.sidebar:
    st.header("Navigation")
    # Navigation styling
    st.markdown("""
        <style>
        .nav-link {
            padding: 10px;
            border-radius: 5px;
            background-color: #f0f2f6;
            margin-bottom: 10px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .nav-link:hover {
            background-color: #e0e2e6;
        }
        .nav-selected {
            background-color: #e0e2e6;
            border-left: 4px solid #ff4b4b;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create navigation options with icons
    if st.button("📤 Upload", key="nav_upload", 
        use_container_width=True,
        help="Upload new documents"):
        st.session_state.page = "upload"
        st.rerun()
    
    if st.button("📋 Documents", key="nav_docs",
        use_container_width=True,
        help="View and manage documents"):
        st.session_state.page = "documents"
        st.rerun()
        
    if st.button("⚙️ Configuration", key="nav_config",
        use_container_width=True,
        help="Manage categories and tags"):
        st.session_state.page = "config"
        st.rerun()

# Show the selected page
if st.session_state.page == "upload":
    show_upload_page()
elif st.session_state.page == "documents":
    show_documents_page()
elif st.session_state.page == "config":
    show_config_page() 