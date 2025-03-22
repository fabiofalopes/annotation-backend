#!/usr/bin/env python3
import streamlit as st
import os
import sys
import importlib

# Add the admin_ui directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(script_dir))

# Import admin client
from admin_ui.admin import AnnoBackendAdmin

# Set page configuration
st.set_page_config(
    page_title="Annotation Backend Admin",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for authentication and navigation
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "token" not in st.session_state:
    st.session_state.token = None
if "admin" not in st.session_state:
    st.session_state.admin = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "import_data"

def login(username: str, password: str):
    """Handle login and return success status"""
    try:
        api_url = os.environ.get('ANNO_API_URL')
        st.sidebar.info(f"Connecting to API at: {api_url}")
        admin = AnnoBackendAdmin(base_url=api_url)
        token = admin.login(username, password)
        st.session_state.authenticated = True
        st.session_state.token = token
        st.session_state.admin = admin
        return True
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg:
            st.error("Login failed: Invalid username or password")
        elif "Connection" in error_msg:
            st.error(f"Could not connect to the API server at {api_url}. Please check if the server is running.")
        else:
            st.error(f"Login failed: {e}")
        return False

def logout():
    """Handle logout"""
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.admin = None
    st.rerun()

def render_login():
    """Render login form"""
    st.title("Annotation Backend Admin")
    st.write("Please log in to access the admin interface.")
    
    with st.sidebar:
        st.title("Admin Dashboard")
        st.info("Please log in to continue")
        st.caption(f"API: {os.environ.get('ANNO_API_URL')}")
        
        st.header("Login")
        username = st.text_input("Username", value="admin", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_button"):
            if login(username, password):
                st.success("Logged in successfully!")
                st.rerun()

def clear_view_state(view_name):
    """Clear session state keys for a specific view"""
    keys_to_remove = [
        key for key in st.session_state.keys()
        if key.startswith(f"{view_name}_")
    ]
    for key in keys_to_remove:
        del st.session_state[key]

def load_view(view_name):
    """Dynamically import and execute view module"""
    try:
        # If we're changing views, clear the old view's state
        if "previous_view" in st.session_state:
            if st.session_state.previous_view != view_name:
                clear_view_state(st.session_state.previous_view)
        
        # Update the previous view
        st.session_state.previous_view = view_name
        
        # Import the view module
        view_module = importlib.import_module(f"admin_ui.views.{view_name}")
        
        # Force reload to ensure we get the latest version
        importlib.reload(view_module)
    except Exception as e:
        st.error(f"Error loading view '{view_name}': {e}")

def render_navigation():
    """Render the navigation sidebar"""
    with st.sidebar:
        st.title("Admin Dashboard")
        
        # Auth status and API info
        cols = st.columns([3, 1])
        with cols[0]:
            st.success("Authenticated ✓")
            st.caption(f"API: {os.environ.get('ANNO_API_URL')}")
        with cols[1]:
            if st.button("Logout", type="secondary", use_container_width=True):
                logout()
        
        st.divider()
        
        # Navigation
        st.subheader("Navigation")
        
        # Define the available pages
        pages = {
            "import_data": {"icon": "📥", "title": "Import Data"},
            "projects": {"icon": "📁", "title": "Projects"},
            "containers": {"icon": "🗄️", "title": "Containers"},
            "users": {"icon": "👥", "title": "Users"}
        }
        
        # Create navigation buttons
        for page_id, page_info in pages.items():
            is_active = st.session_state.current_page == page_id
            button_type = "primary" if is_active else "secondary"
            
            if st.button(
                f"{page_info['icon']} {page_info['title']}", 
                key=f"nav_{page_id}",
                type=button_type,
                use_container_width=True
            ):
                # Clear the current view's state before changing pages
                if "current_page" in st.session_state:
                    clear_view_state(st.session_state.current_page)
                st.session_state.current_page = page_id
                st.rerun()

def main():
    # If not authenticated, show login page
    if not st.session_state.authenticated:
        render_login()
    else:
        # Render navigation sidebar
        render_navigation()
        
        # Load the current view
        load_view(st.session_state.current_page)

if __name__ == "__main__":
    main() 