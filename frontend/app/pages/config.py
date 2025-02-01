import streamlit as st
from app.components.utils import (
    run_async_operation,
    invalidate_categories_cache,
    DOCUMENT_ICONS,
    invalidate_tags_cache
)

def show_config_page(api):
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
            icon_label = st.selectbox(
                "Icon",
                options=list(DOCUMENT_ICONS.keys()),
                format_func=lambda x: f"{DOCUMENT_ICONS[x]} {x.split(' ')[1]}"
            )
            new_category_icon = DOCUMENT_ICONS[icon_label]
        
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
                invalidate_categories_cache()  # Invalidate cache after adding
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
                                invalidate_categories_cache()  # Invalidate cache after deleting
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