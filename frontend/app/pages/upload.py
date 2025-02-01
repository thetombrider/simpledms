import streamlit as st
from app.components.utils import (
    run_async_operation,
    get_categories,
    get_tags,
    invalidate_tags_cache,
    TEMP_USER_ID
)

def show_upload_page(api):
    """Upload page content"""
    st.header("Upload Document")
    
    # Initialize state for new tag input if not exists
    if 'new_tag_input' not in st.session_state:
        st.session_state.new_tag_input = ""
    if 'current_tags' not in st.session_state:
        st.session_state.current_tags = []
    
    with st.form("upload_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_file = st.file_uploader("Choose a file", type=None)
            title = st.text_input("Title")
            description = st.text_area("Description")
        
        with col2:
            categories = st.multiselect(
                "Categories",
                options=get_categories(st.session_state.categories_cache_version, api),
                default=[]
            )
            
            # Get existing tags for suggestions
            existing_tags = get_tags(st.session_state.tags_cache_version, api)
            
            # Create two columns for tag input
            tag_col1, tag_col2 = st.columns([3, 1])
            
            with tag_col1:
                # Selected tags multiselect
                tags = st.multiselect(
                    "Tags",
                    options=existing_tags + st.session_state.current_tags,
                    default=st.session_state.current_tags,
                    help="Select from existing tags or add new ones below"
                )
                
                # New tag input
                new_tag = st.text_input("Add new tag", key="new_tag_field", value=st.session_state.new_tag_input)
            
            with tag_col2:
                # Add new tag button
                if st.form_submit_button("Add Tag", use_container_width=True):
                    if new_tag and new_tag not in tags and new_tag not in existing_tags:
                        try:
                            # Create the new tag in the database
                            run_async_operation(
                                lambda: api.create_tag(new_tag, "#808080")  # Default color for new tags
                            )
                            invalidate_tags_cache()  # Update tags cache
                            # Add to current tags
                            st.session_state.current_tags = list(set(tags + [new_tag]))
                            st.session_state.new_tag_input = ""  # Clear input
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error creating new tag '{new_tag}': {str(e)}")
        
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
                        # Reset tag state after successful upload
                        st.session_state.current_tags = []
                    except Exception as e:
                        st.error(f"Error uploading document: {str(e)}") 