#!/usr/bin/env python3
import streamlit as st
import os
import sys
import traceback
from admin_ui.utils.ui_components import notification

# Set page configuration *FIRST*
st.set_page_config(
    page_title="Annotation Backend Admin",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add the admin_ui directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(script_dir))

# Import admin client
from admin_ui.api_client import AnnoBackendAdmin

# Import the view modules *here*
from admin_ui.views import projects, containers, users, import_data

# Initialize session state - much simpler now
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "admin" not in st.session_state:
    st.session_state["admin"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "projects"  # Start with projects

# Get admin API URL from environment
admin_api_url = os.environ.get("ADMIN_API_URL", "http://annotation_api:8000")

# No more request ID approach

def login(username: str, password: str):
    """Handle login and return success status"""
    try:
        api_url = os.environ.get('ANNO_API_URL', admin_api_url)
        st.sidebar.info(f"Connecting to API at: {api_url}")
        admin = AnnoBackendAdmin(base_url=api_url)
        admin.login(username, password)  # Don't need to store the token separately
        st.session_state.authenticated = True
        st.session_state.admin = admin
        return True
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg:
            st.error("Login failed: Invalid username or password")
        elif "Connection" in error_msg:
            st.error(f"Could not connect to the API server at: {api_url}. Please check if the server is running.")
        else:
            st.error(f"Login failed: {e}")
        return False

def logout():
    """Handle logout"""
    st.session_state.authenticated = False
    st.session_state.admin = None
    # No need to clear view cache
    st.rerun()

def render_login():
    """Render login form"""
    st.title("Annotation Backend Admin")
    st.write("Please log in to access the admin interface.")

    with st.sidebar:
        st.title("Admin Dashboard")
        st.info("Please log in to continue")
        st.caption(f"API: {os.environ.get('ANNO_API_URL')}")

        with st.form(key="login_form"): # Simplified form key
            st.header("Login")
            username = st.text_input("Username", value="admin")
            password = st.text_input("Password", type="password")

            login_button = st.form_submit_button("Login")

            if login_button:
                if login(username, password):
                    st.success("Logged in successfully!")
                    st.rerun()

def render_navigation():
    """Render the navigation sidebar"""
    with st.sidebar:
        st.title("Admin Dashboard")

        # Auth status and API info
        if st.session_state.authenticated:
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
            "projects": {"icon": "📁", "title": "Projects"},
            "containers": {"icon": "🗄️", "title": "Containers"},
            "users": {"icon": "👥", "title": "Users"},
            "import_data": {"icon": "📥", "title": "Import Data"}, # Keep import_data for now
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
                st.session_state.current_page = page_id
                st.rerun()


def main():
    # If not authenticated, show login page
    if not st.session_state.authenticated:
        render_login()
    else:
        # Render navigation sidebar
        render_navigation()

        # *Directly* call the appropriate show_ function
        if st.session_state.current_page == "projects":
            projects.show_projects_view()
        elif st.session_state.current_page == "containers":
            containers.show_containers_view()
        elif st.session_state.current_page == "users":
            users.show_users_view()
        elif st.session_state.current_page == "import_data":
            import_data.show_import_data_view()

if __name__ == "__main__":
    main() 