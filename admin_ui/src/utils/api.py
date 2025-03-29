"""
API utilities for the admin UI.
Provides functions for API URL management and authentication headers.
"""

import os
import streamlit as st
from typing import Dict
from config.settings import API_BASE_URL

def get_api_url() -> str:
    """Get the base API URL from environment variable or use default"""
    return API_BASE_URL

def get_auth_header(token: str = None) -> Dict[str, str]:
    """
    Get authentication header for API requests.
    If token is not provided, tries to get it from session state.
    """
    if token is None:
        token = st.session_state.get("token")
        if not token:
            st.error("No authentication token found")
            return {}
    
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    } 