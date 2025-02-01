import streamlit as st
from app.api.document_api import DocumentAPI
from app.components.navigation import show_navigation
from app.components.utils import init_cache_state, API_URL
from app.pages.upload import show_upload_page
from app.pages.documents import show_documents_page
from app.pages.config import show_config_page
from app.pages.user import show_user_page

# Initialize API client
api = DocumentAPI(API_URL)

# Set page config
st.set_page_config(
    page_title="SimpleS3DMS",
    page_icon="📄",
    layout="wide"
)

# Title
st.title("📄 SimpleS3DMS")
st.subheader("Simple Document Management System")

# Initialize cache state
init_cache_state()

# Initialize page in session state if not exists
if "page" not in st.session_state:
    st.session_state.page = "upload"

# Show navigation menu
show_navigation()

# Show the selected page
if st.session_state.page == "upload":
    show_upload_page(api)
elif st.session_state.page == "documents":
    show_documents_page(api)
elif st.session_state.page == "config":
    show_config_page(api)
elif st.session_state.page == "user":
    show_user_page(api) 