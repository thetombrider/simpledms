import streamlit as st
from app.components.utils import run_async_operation, get_categories, TEMP_USER_ID

def show_documents_page(api):
    """Documents page content"""
    st.header("My Documents")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        filter_category = st.selectbox(
            "Filter by category",
            ["All"] + get_categories(st.session_state.categories_cache_version, api)
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