import streamlit as st
import os
from admin_ui.admin import AnnoBackendAdmin

def initialize_auth():
    """Initialize authentication session state"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "token" not in st.session_state:
        st.session_state.token = None
    if "admin" not in st.session_state:
        st.session_state.admin = None

def login(username: str, password: str) -> bool:
    """Handle login and return success status"""
    try:
        api_url = os.environ.get('ANNO_API_URL')
        st.sidebar.info(f"Attempting to connect to API at: {api_url}")
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

def render_auth():
    """Render authentication form"""
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username", value="admin", key="login_username")
    password = st.sidebar.text_input("Password", type="password", key="login_password")
    
    if st.sidebar.button("Login", key="login_button"):
        if login(username, password):
            st.sidebar.success("Logged in successfully!")
            st.rerun() 