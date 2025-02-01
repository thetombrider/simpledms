import asyncio
import streamlit as st
import re
from pathlib import Path
from typing import List

# Constants
API_URL = "http://localhost:8080/api/v1"  # Updated port to match backend
TEMP_USER_ID = "test_user"  # We'll replace this with real auth later
DOCUMENT_ICONS = {
    "📄 Document": "📄",
    "📝 Note": "📝",
    "📊 Chart": "📊",
    "📈 Graph": "📈",
    "📑 Files": "📑",
    "📋 Clipboard": "📋",
    "📎 Attachment": "📎",
    "📌 Pin": "📌",
    "📁 Folder": "📁",
    "💼 Briefcase": "💼",
    "📧 Email": "📧",
    "📃 Contract": "📃",
    "🧾 Receipt": "🧾",
    "📜 Scroll": "📜",
    "📰 News": "📰",
    "📓 Notebook": "📓"
}

def run_async_operation(func, *args, **kwargs):
    """Helper function to run async operations"""
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

def format_size(size_in_bytes: int) -> str:
    """Format size in bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.1f} TB"

# Cache management functions
def init_cache_state():
    """Initialize cache version in session state"""
    if 'categories_cache_version' not in st.session_state:
        st.session_state.categories_cache_version = 0
    if 'tags_cache_version' not in st.session_state:
        st.session_state.tags_cache_version = 0

def invalidate_categories_cache():
    """Increment the cache version to force a refresh of categories"""
    st.session_state.categories_cache_version += 1

def invalidate_tags_cache():
    """Increment the cache version to force a refresh of tags"""
    st.session_state.tags_cache_version += 1

# Cache decorators
@st.cache_data(ttl=60)  # Reduced cache time to 1 minute for more frequent updates
def get_categories(cache_version: int, _api) -> List[str]:
    """Get list of category names from the database"""
    try:
        categories = run_async_operation(_api.list_categories)
        return [cat["name"] for cat in categories] if categories else ["Invoice", "Contract", "Report", "Other"]
    except Exception as e:
        st.error(f"Error loading categories: {str(e)}")
        return ["Invoice", "Contract", "Report", "Other"]

@st.cache_data(ttl=60)  # Reduced cache time to 1 minute for more frequent updates
def get_tags(cache_version: int, _api) -> List[str]:
    """Get list of tag names from the database"""
    try:
        tags = run_async_operation(_api.list_tags)
        return [tag["name"] for tag in tags] if tags else []
    except Exception as e:
        st.error(f"Error loading tags: {str(e)}")
        return []

def generate_title_from_filename(filename: str) -> str:
    """Generate a clean title from a filename"""
    # Remove file extension
    title = Path(filename).stem
    
    # Replace underscores and hyphens with spaces
    title = title.replace('_', ' ').replace('-', ' ')
    
    # Remove any special characters except spaces
    title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
    
    # Convert to title case and strip extra spaces
    title = ' '.join(word.capitalize() for word in title.split())
    
    return title