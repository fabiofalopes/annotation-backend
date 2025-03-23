"""
Main entry point for the Admin UI application.
"""
import os
import streamlit as st
from typing import Optional

from admin_ui.views import users, projects, containers, import_data
from admin_ui.utils.ui_components import notification

# Page configuration
st.set_page_config(
    page_title="Anno Backend Admin",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.admin = None
    st.session_state.current_page = "users"  # Default page

def initialize_api_client(api_url: str, username: str, password: str) -> Optional[bool]:
    """Initialize the API client with credentials.
    
    Args:
        api_url: The base URL for the API
        username: Admin username
        password: Admin password
        
    Returns:
        bool: True if authentication successful, False otherwise
    """
    try:
        from admin_ui.api_client import AnnoBackendAdmin
        admin = AnnoBackendAdmin(api_url)
        if admin.login(username, password):
            st.session_state.admin = admin
            st.session_state.authenticated = True
            st.session_state.token = admin.token  # Store the token in session state
            return True
        return False
    except Exception as e:
        notification(f"Authentication error: {str(e)}", "error")
        return False

def check_auth():
    """Check if the user is authenticated and the token is valid."""
    if not st.session_state.authenticated or not st.session_state.admin:
        return False
    
    # Check if token exists in session state
    if not st.session_state.get("token"):
        return False
    
    return True

def render_login_form():
    """Render the login form."""
    st.title("Anno Backend Admin")
    
    with st.form("login_form"):
        api_url = st.text_input(
            "API URL",
            value=os.getenv("ANNO_API_URL", "http://localhost:8000")
        )
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Login"):
            if initialize_api_client(api_url, username, password):
                notification("Successfully logged in!", "success")
                st.rerun()  # Force rerun to show the main interface
            else:
                notification("Invalid credentials", "error")

def render_navigation():
    """Render the navigation sidebar."""
    with st.sidebar:
        st.title("Navigation")
        
        # Navigation buttons
        if st.button("Users", use_container_width=True):
            st.session_state.current_page = "users"
            
        if st.button("Projects", use_container_width=True):
            st.session_state.current_page = "projects"
            
        if st.button("Containers", use_container_width=True):
            st.session_state.current_page = "containers"
            
        if st.button("Import Data", use_container_width=True):
            st.session_state.current_page = "import_data"
        
        # Logout button at the bottom
        st.sidebar.markdown("---")
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.admin = None
            st.session_state.token = None
            st.rerun()

def main():
    """Main application entry point."""
    if not check_auth():
        render_login_form()
    else:
        render_navigation()
        
        # Render the appropriate view based on current_page
        if st.session_state.current_page == "users":
            users.show_users_view()
        elif st.session_state.current_page == "projects":
            projects.show_projects_view()
        elif st.session_state.current_page == "containers":
            containers.show_containers_view()
        elif st.session_state.current_page == "import_data":
            import_data.show_import_data_view()

if __name__ == "__main__":
    main() 