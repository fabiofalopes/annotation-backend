import requests
from typing import Optional, Dict, Any
import streamlit as st
from config.settings import API_BASE_URL, ADMIN_API_URL

def show_notification(message: str, type: str = "info"):
    """Show a notification using Streamlit's built-in functions"""
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    else:
        st.info(message)

def get_auth_header(token: str) -> dict:
    """Get the authorization header for API requests"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def api_request(method: str, endpoint: str, token: str, data: Dict = None) -> Optional[Dict]:
    """Generic API request handler with error handling"""
    try:
        url = f"{ADMIN_API_URL}/{endpoint.lstrip('/')}"
        headers = get_auth_header(token)
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Print request details for debugging
        print(f"Request: {method} {url}")
        print(f"Headers: {headers}")
        if data:
            print(f"Data: {data}")
        print(f"Response: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code >= 400:
            error_msg = response.json().get('detail', response.text) if response.text else 'Unknown error'
            show_notification(f"API Error: {error_msg}", "error")
            return None
            
        return response.json() if response.content else None
    except requests.exceptions.RequestException as e:
        show_notification(f"API Error: {str(e)}", "error")
        return None

def login(username: str, password: str) -> Optional[str]:
    """Login to get access token"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/token",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code >= 400:
            error_msg = response.json().get('detail', response.text) if response.text else 'Unknown error'
            show_notification(f"Login failed: {error_msg}", "error")
            return None
            
        return response.json().get("access_token")
    except Exception as e:
        show_notification(f"Login failed: {str(e)}", "error")
        return None 