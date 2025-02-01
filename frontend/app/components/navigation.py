import streamlit as st

def show_navigation():
    """Show the navigation menu"""
    with st.sidebar:
        st.title("SimpleS3DMS")
        
        # Navigation buttons
        with st.form("navigation_form"):
            if st.form_submit_button("📤 Upload", use_container_width=True):
                st.session_state.page = "upload"
                st.rerun()
                
            if st.form_submit_button("📄 Documents", use_container_width=True):
                st.session_state.page = "documents"
                st.rerun()
                
            if st.form_submit_button("⚙️ Configuration", use_container_width=True):
                st.session_state.page = "config"
                st.rerun()
                
            if st.form_submit_button("👤 User Profile", use_container_width=True):
                st.session_state.page = "user"
                st.rerun()
            
        st.markdown("---")
        st.caption("Version 0.1.0") 