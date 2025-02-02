import streamlit as st
from app.components.utils import (
    run_async_operation,
    get_categories,
    get_tags,
    invalidate_categories_cache,
    invalidate_tags_cache,
    generate_title_from_filename,
    TEMP_USER_ID
)

def show_upload_page(api):
    """Upload page content"""
    st.header("Upload Documents")
    
    # Check backend connectivity
    try:
        # Initialize state for new tag input if not exists
        if 'new_tag_input' not in st.session_state:
            st.session_state.new_tag_input = ""
        if 'current_tags' not in st.session_state:
            st.session_state.current_tags = []
        if 'suggested_title' not in st.session_state:
            st.session_state.suggested_title = ""
        if 'last_files' not in st.session_state:
            st.session_state.last_files = None
        if 'suggested_description' not in st.session_state:
            st.session_state.suggested_description = ""
        if 'suggested_categories' not in st.session_state:
            st.session_state.suggested_categories = []
        if 'suggested_tags' not in st.session_state:
            st.session_state.suggested_tags = []
        
        # Force cache refresh on page load
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = 0
            invalidate_categories_cache()
            invalidate_tags_cache()
        
        # File uploader outside the form
        uploaded_files = st.file_uploader(
            "Choose files",
            type=None,
            accept_multiple_files=True,
            help="You can select multiple files"
        )
        
        # Update suggested title if files changed
        if uploaded_files != st.session_state.last_files:
            st.session_state.last_files = uploaded_files
            if not uploaded_files:
                st.session_state.suggested_title = ""
            elif len(uploaded_files) == 1:
                st.session_state.suggested_title = generate_title_from_filename(uploaded_files[0].name)
            else:
                # For multiple files, find common prefix
                filenames = [generate_title_from_filename(f.name) for f in uploaded_files]
                common_words = set(filenames[0].split())
                for name in filenames[1:]:
                    common_words &= set(name.split())
                
                if common_words:
                    # Use common words as prefix
                    st.session_state.suggested_title = ' '.join(sorted(common_words))
                else:
                    # If no common words, use date-based prefix
                    from datetime import datetime
                    st.session_state.suggested_title = f"Documents {datetime.now().strftime('%Y-%m-%d')}"
        
        # AI Analysis section (outside form)
        if uploaded_files and len(uploaded_files) == 1:
            if st.button("Analyze Document with AI", key="analyze_button"):
                with st.spinner("Analyzing document..."):
                    try:
                        analysis = run_async_operation(
                            api.analyze_document,
                            uploaded_files[0]
                        )
                        st.session_state.suggested_description = analysis["summary"]
                        st.session_state.suggested_categories = analysis["categories"]
                        st.session_state.suggested_tags = analysis["tags"]
                        st.success("Document analyzed successfully!")
                    except ValueError as e:
                        if "OPENAI_API_KEY" in str(e):
                            st.error("OpenAI API key not configured. Please add it to your .env file.")
                        else:
                            st.error(f"Could not analyze document: {str(e)}")
                        st.session_state.suggested_description = ""
                        st.session_state.suggested_categories = []
                        st.session_state.suggested_tags = []
        
        with st.form("upload_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                # Use suggested title as default if available
                title_prefix = st.text_input(
                    "Document Title",
                    value=st.session_state.suggested_title,
                    help="Enter the document title. For multiple files, this will be used as prefix followed by a number (e.g. 'Invoice' becomes 'Invoice 1', 'Invoice 2', etc.)"
                )
                description = st.text_area(
                    "Description",
                    value=st.session_state.suggested_description,
                    help="AI-generated description will be suggested when available"
                )
            
            with col2:
                # Get categories with cache version
                available_categories = get_categories(st.session_state.categories_cache_version, api)
                # Filter suggested categories to only include available ones
                filtered_suggested_categories = [
                    cat for cat in st.session_state.suggested_categories 
                    if cat in available_categories
                ]
                
                categories = st.multiselect(
                    "Categories",
                    options=available_categories,
                    default=filtered_suggested_categories,
                    help="AI-suggested categories will be pre-selected when available"
                )
                
                # Get existing tags for suggestions with cache version
                existing_tags = get_tags(st.session_state.tags_cache_version, api)
                suggested_tags = st.session_state.suggested_tags
                
                # Create two columns for tag input
                tag_col1, tag_col2 = st.columns([3, 1])
                
                with tag_col1:
                    # Selected tags multiselect
                    tags = st.multiselect(
                        "Tags",
                        options=existing_tags + st.session_state.current_tags + suggested_tags,
                        default=suggested_tags,
                        help="AI-suggested tags will be pre-selected when available"
                    )
                    
                    # New tag input
                    new_tag = st.text_input("Add new tag", key="new_tag_field", value=st.session_state.new_tag_input)
                
                with tag_col2:
                    # Add new tag button
                    add_tag = st.form_submit_button("Add Tag", use_container_width=True)
                    if add_tag:
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
            
            # Main form submit button
            submit = st.form_submit_button("Upload Documents", use_container_width=True)
            
            if submit:
                if not uploaded_files:
                    st.error("Please select at least one file to upload")
                elif not title_prefix:
                    st.error("Please provide a title prefix")
                else:
                    with st.spinner(f"Uploading {len(uploaded_files)} document(s)..."):
                        try:
                            documents = run_async_operation(
                                api.upload_documents,
                                uploaded_files,
                                title_prefix,
                                description,
                                categories,
                                tags,
                                TEMP_USER_ID
                            )
                            st.success(f"Successfully uploaded {len(documents)} document(s)!")
                            
                            # Show uploaded documents summary
                            with st.expander("View uploaded documents"):
                                for doc in documents:
                                    st.write(f"📄 {doc['title']} ({doc['file_name']})")
                                    st.caption(f"Size: {doc['file_size']} bytes")
                            
                            # Reset states after successful upload
                            st.session_state.current_tags = []
                            st.session_state.suggested_title = ""
                            st.session_state.last_files = None
                            st.session_state.suggested_description = ""
                            st.session_state.suggested_categories = []
                            st.session_state.suggested_tags = []
                            st.session_state.new_tag_input = ""
                            # Force cache refresh after upload
                            invalidate_categories_cache()
                            invalidate_tags_cache()
                            # Clear the file uploader
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error uploading documents: {str(e)}")
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")

    st.write("This is the upload page content") 