#!/usr/bin/env python3
import streamlit as st
import os
import sys

# Add the admin_ui directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(script_dir))

# Import components
from admin_ui.components.auth import initialize_auth, render_auth
from admin_ui.components.navigation import render_sidebar
from admin_ui.pages.users import render_users_page
from admin_ui.pages.projects import render_projects_page
from admin_ui.pages.containers import render_containers_page
from admin_ui.pages.import_data import render_import_page

# Set page configuration
st.set_page_config(
    page_title="Annotation Backend Admin",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Initialize authentication state
    initialize_auth()
    
    # Render sidebar navigation
    render_sidebar()
    
    # Show appropriate page based on navigation
    if not st.session_state.authenticated:
        st.title("Annotation Backend Admin")
        st.write("Please log in using the sidebar to access the admin interface.")
        render_auth()
    else:
        if not hasattr(st.session_state, 'current_page'):
            st.session_state.current_page = "users"
        
        # Render the appropriate page
        if st.session_state.current_page == "users":
            render_users_page()
        elif st.session_state.current_page == "projects":
            render_projects_page()
        elif st.session_state.current_page == "containers":
            render_containers_page()
        elif st.session_state.current_page == "import":
            render_import_page()

if __name__ == "__main__":
    main() 