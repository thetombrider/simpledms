import streamlit as st
from app.components.utils import run_async_operation, format_size, TEMP_USER_ID

def show_user_page(api):
    """User profile page content"""
    st.header("User Profile")
    
    # User info section
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image("https://api.dicebear.com/7.x/initials/svg?seed=" + TEMP_USER_ID, width=150)
        with col2:
            st.subheader(TEMP_USER_ID)  # Will be replaced with actual user info
            st.caption("Member since: Coming soon with auth")
    
    # Get user statistics
    try:
        stats = run_async_operation(lambda: api.get_user_stats(TEMP_USER_ID))
        
        # Main KPIs
        st.subheader("Document Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Documents", stats["total_documents"])
        with col2:
            st.metric("Total Storage", format_size(stats["total_size"]))
        with col3:
            st.metric("Most Used Category", stats["most_used_category"] or "None")
        with col4:
            st.metric("Most Used Tag", stats["most_used_tag"] or "None")
        
        # Detailed statistics
        col1, col2 = st.columns(2)
        
        with col1:
            # Category distribution
            st.subheader("Categories Distribution")
            if stats["categories_distribution"]:
                for cat, count in stats["categories_distribution"].items():
                    st.caption(f"{cat}: {count} documents")
            else:
                st.caption("No categories used yet")
        
        with col2:
            # Tag distribution
            st.subheader("Tags Distribution")
            if stats["tags_distribution"]:
                for tag, count in stats["tags_distribution"].items():
                    st.caption(f"{tag}: {count} documents")
            else:
                st.caption("No tags used yet")
        
        # Documents by month
        st.subheader("Documents by Month")
        if stats["documents_by_month"]:
            # Convert to list for charting
            months = list(stats["documents_by_month"].keys())
            counts = list(stats["documents_by_month"].values())
            
            # Create a bar chart
            st.bar_chart(stats["documents_by_month"])
        else:
            st.caption("No documents uploaded yet")
            
    except Exception as e:
        st.error(f"Error loading user statistics: {str(e)}")

    # Future sections (to be implemented with auth)
    with st.expander("Account Settings (Coming Soon)"):
        st.write("- Change password")
        st.write("- Update profile")
        st.write("- Notification preferences")
        st.write("- API keys management") 