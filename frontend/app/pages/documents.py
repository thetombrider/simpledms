import streamlit as st
from datetime import datetime, timezone
from app.components.utils import run_async_operation, get_categories, TEMP_USER_ID

def format_expiry(expiry_date: str) -> str:
    """Format expiry date and calculate time remaining"""
    expiry = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    remaining = expiry - now
    
    if remaining.days > 0:
        return f"Expires in {remaining.days} days"
    elif remaining.seconds > 3600:
        hours = remaining.seconds // 3600
        return f"Expires in {hours} hours"
    elif remaining.seconds > 60:
        minutes = remaining.seconds // 60
        return f"Expires in {minutes} minutes"
    else:
        return "Expires soon"

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
        
        # Get all shares for the user
        shares = run_async_operation(
            api.list_shares,
            owner_id=TEMP_USER_ID,
            include_expired=False
        )
        
        # Create a map of document_id to share info
        share_map = {share["document_id"]: share for share in shares}
        
        if not documents:
            st.info("No documents found")
        else:
            for doc in documents:
                with st.expander(f"{doc['title']} ({doc['file_name']})"):
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        st.write(f"Description: {doc['description']}")
                        st.write(f"Categories: {', '.join(doc['categories'])}")
                        st.write(f"Tags: {', '.join(doc['tags'])}")
                        st.write(f"Size: {doc['file_size']} bytes")
                        st.write(f"Uploaded: {doc['created_at']}")
                        
                        # Show share info if exists
                        if doc["_id"] in share_map:
                            share = share_map[doc["_id"]]
                            st.markdown(f"🔗 **Shared link:** [{share['short_url']}]({share['short_url']})")
                            st.caption(format_expiry(share['expires_at']))
                    
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
                        # Share button and functionality
                        if doc["_id"] not in share_map:
                            if st.button("Share", key=f"share_{doc['_id']}"):
                                with st.spinner("Creating share link..."):
                                    try:
                                        share = run_async_operation(
                                            api.create_share,
                                            doc['_id'],
                                            TEMP_USER_ID
                                        )
                                        # Create a new container for the share info
                                        share_info = st.container()
                                        with share_info:
                                            st.success("Share link created!")
                                            st.markdown(f"🔗 **Share link:** [{share['short_url']}]({share['short_url']})")
                                            st.caption(format_expiry(share['expires_at']))
                                            # Add copy button
                                            st.code(share['short_url'], language=None)
                                        # Don't rerun immediately, let the user see the share info
                                        st.session_state[f"show_share_{doc['_id']}"] = True
                                    except Exception as e:
                                        st.error(f"Error creating share link: {str(e)}")
                        else:
                            # Delete share button
                            if st.button("Unshare", key=f"unshare_{doc['_id']}"):
                                with st.spinner("Removing share link..."):
                                    try:
                                        share = share_map[doc["_id"]]
                                        run_async_operation(
                                            api.delete_share,
                                            share['id'],
                                            TEMP_USER_ID
                                        )
                                        st.success("Share link removed!")
                                        st.rerun()  # Refresh to remove share
                                    except Exception as e:
                                        st.error(f"Error removing share link: {str(e)}")
                    
                    with col4:
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
                                            # Delete any existing shares first
                                            if doc["_id"] in share_map:
                                                share = share_map[doc["_id"]]
                                                run_async_operation(
                                                    api.delete_share,
                                                    share['id'],
                                                    TEMP_USER_ID
                                                )
                                            
                                            # Then delete the document
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