"""
Authentication utilities for the admin UI.
Provides functions for authentication and access control.
"""

import streamlit as st
import requests
from typing import Optional
from .api import get_api_url, get_auth_header
from config.settings import API_BASE_URL

def check_auth() -> bool:
    """Check if user is authenticated"""
    if "token" not in st.session_state:
        st.session_state.token = None
    
    if not st.session_state.token:
        render_login_form()
        return False
    
    return True

def check_admin_access() -> bool:
    """Check if current user has admin access"""
    if not check_auth():
        return False
    
    # For now, we'll assume any authenticated user has admin access
    return True

def render_login_form():
    """Render the login form"""
    st.title("🔐 Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if login(username, password):
                st.rerun()

def login(username: str, password: str) -> bool:
    """Attempt to log in user and get access token"""
    try:
        # Send as form data, not JSON
        response = requests.post(
            f"{API_BASE_URL}/auth/token",
            data={
                "grant_type": "password",
                "username": username,
                "password": password
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                st.session_state.token = token
                return True
            else:
                st.error("No access token in response")
                return False
        else:
            st.error(f"Login failed: {response.text}")
            return False
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return False

def logout():
    """Log out the current user"""
    st.session_state.token = None 