import streamlit as st
import os
from admin_ui.components.auth import logout

def refresh_data():
    """Refresh data for the current page"""
    try:
        if hasattr(st.session_state, 'current_page'):
            if st.session_state.current_page == "users":
                st.session_state.users = st.session_state.admin.list_users()
            elif st.session_state.current_page == "projects":
                st.session_state.projects = st.session_state.admin.list_projects()
            elif st.session_state.current_page == "containers":
                st.session_state.containers = st.session_state.admin.list_containers()
    except Exception as e:
        st.error(f"Error refreshing data: {e}")

def render_sidebar():
    """Render the navigation sidebar"""
    st.sidebar.title("Navigation")
    
    # Display API URL (but don't allow editing)
    st.sidebar.text(f"API URL: {os.environ.get('ANNO_API_URL')}")
    
    # If authenticated, show navigation menu
    if st.session_state.authenticated:
        st.sidebar.success("Authenticated ✓")
        if st.sidebar.button("Logout", key="logout_button"):
            logout()
        
        # Navigation buttons
        st.sidebar.header("Manage")
        if st.sidebar.button("Users", key="nav_users_button"):
            st.session_state.current_page = "users"
            refresh_data()
            st.rerun()
        if st.sidebar.button("Projects", key="nav_projects_button"):
            st.session_state.current_page = "projects"
            refresh_data()
            st.rerun()
        if st.sidebar.button("Data Containers", key="nav_containers_button"):
            st.session_state.current_page = "containers"
            refresh_data()
            st.rerun()
        if st.sidebar.button("Import Data", key="nav_import_button"):
            st.session_state.current_page = "import"
            st.rerun() 