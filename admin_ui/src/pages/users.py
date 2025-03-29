import streamlit as st
import pandas as pd
import requests
from typing import Dict, List, Optional
import re
from st_aggrid import AgGrid, GridOptionsBuilder
from datetime import datetime

from utils.api import get_api_url, get_auth_header
from utils.auth import check_admin_access
from config.settings import API_BASE_URL

# API endpoints
USERS_ENDPOINT = f"{API_BASE_URL}/admin-api/users"
PROJECTS_ENDPOINT = f"{API_BASE_URL}/admin-api/projects"

def get_users(token: str) -> List[Dict]:
    """Fetch users from the API"""
    try:
        response = requests.get(
            USERS_ENDPOINT,
            headers=get_auth_header(token)
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch users: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error fetching users: {str(e)}")
        return []

def create_user(token: str, user_data: Dict) -> bool:
    """Create a new user via API"""
    try:
        response = requests.post(
            USERS_ENDPOINT,
            headers=get_auth_header(token),
            json=user_data
        )
        if response.status_code == 200:
            st.success("User created successfully!")
            return True
        else:
            st.error(f"Failed to create user: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error creating user: {str(e)}")
        return False

def delete_user(token: str, user_id: int) -> bool:
    """Delete a user via API"""
    try:
        response = requests.delete(
            f"{USERS_ENDPOINT}/{user_id}",
            headers=get_auth_header(token)
        )
        if response.status_code == 204:
            st.success("User deleted successfully!")
            return True
        else:
            st.error(f"Failed to delete user: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error deleting user: {str(e)}")
        return False

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_username(username: str) -> tuple[bool, str]:
    """Validate username format and length"""
    if not username:
        return False, "Username is required"
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if len(username) > 50:
        return False, "Username must be less than 50 characters"
    if not username.isalnum():
        return False, "Username must contain only letters and numbers"
    return True, ""

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if not password:
        return False, "Password is required"
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    return True, ""

def validate_email_format(email: str, token: str) -> tuple[bool, str]:
    """Validate email format and check for existing users"""
    if not email:
        return False, "Email is required"
    if not validate_email(email):
        return False, "Invalid email format"
    # Check if email already exists
    existing_users = get_users(token)
    if any(user["email"] == email for user in existing_users):
        return False, "Email already registered"
    return True, ""

def render_user_list():
    """Render the user list with AG Grid"""
    st.subheader("👥 Users")
    
    # Get token from session state
    token = st.session_state.get("token")
    if not token:
        st.error("Please log in first")
        return

    # Fetch users
    users = get_users(token)
    if not users:
        return

    # Convert to DataFrame for AG Grid
    df = pd.DataFrame(users)
    if not df.empty:
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Configure grid options
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_columns([
            {"field": "id", "headerName": "ID", "width": 70},
            {"field": "username", "headerName": "Username", "width": 150},
            {"field": "email", "headerName": "Email", "width": 200},
            {"field": "role", "headerName": "Role", "width": 100},
            {"field": "is_active", "headerName": "Active", "width": 100},
            {"field": "created_at", "headerName": "Created At", "width": 180},
        ])
        gb.configure_selection(selection_mode="single")
        gb.configure_grid_options(domLayout="autoHeight")
        grid_options = gb.build()

        # Display grid
        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode="selection_changed",
            fit_columns_on_grid_load=True,
        )
        
        # Handle selected rows
        selected_rows = grid_response["selected_rows"]
        if isinstance(selected_rows, list) and len(selected_rows) > 0:
            user = selected_rows[0]
            with st.expander(f"User Details: {user['username']}", expanded=True):
                # Display user details in a more readable format
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Basic Information**")
                    st.write(f"ID: {user['id']}")
                    st.write(f"Username: {user['username']}")
                    st.write(f"Email: {user['email']}")
                
                with col2:
                    st.write("**Status & Role**")
                    st.write(f"Role: {user['role']}")
                    st.write(f"Active: {'✅' if user['is_active'] else '❌'}")
                    st.write(f"Created: {user['created_at']}")
                
                # Actions section
                st.divider()
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    # Link to detailed view
                    st.page_link(
                        "pages/user_details.py",
                        label="🔍 View Details",
                        query_params={"user_id": user['id']}
                    )
                with col2:
                    if st.button("🗑️ Delete User", type="secondary"):
                        if delete_user(token, user['id']):
                            st.rerun()

def render_create_user_form():
    """Render the create user form with validation"""
    st.subheader("➕ Create New User")
    
    # Get token from session state
    token = st.session_state.get("token")
    if not token:
        st.error("Please log in first")
        return
    
    # Initialize form state in session state if not exists
    if "form_state" not in st.session_state:
        st.session_state.form_state = {
            "username": "",
            "email": "",
            "password": "",
            "role": "annotator"
        }
    
    with st.form("create_user_form"):
        # Username field with validation feedback
        username = st.text_input(
            "Username",
            max_chars=50,
            value=st.session_state.form_state["username"],
            help="3-50 characters, letters and numbers only"
        )
        username_valid, username_error = validate_username(username)
        if username and not username_valid:
            st.error(username_error)
        
        # Email field with validation feedback
        email = st.text_input(
            "Email",
            value=st.session_state.form_state["email"],
            help="Enter a valid email address"
        )
        email_valid, email_error = validate_email_format(email, token)
        if email and not email_valid:
            st.error(email_error)
        
        # Password field with validation feedback
        password = st.text_input(
            "Password",
            type="password",
            value=st.session_state.form_state["password"],
            help="Min 8 chars, must include uppercase, lowercase, and number"
        )
        password_valid, password_error = validate_password(password)
        if password and not password_valid:
            st.error(password_error)
        
        # Role selection
        role = st.selectbox(
            "Role",
            ["annotator", "admin"],
            index=0 if st.session_state.form_state["role"] == "annotator" else 1
        )
        
        # Submit button
        submitted = st.form_submit_button("Create User")
        
        if submitted:
            # Store form state
            st.session_state.form_state = {
                "username": username,
                "email": email,
                "password": password,
                "role": role
            }
            
            # Validate all fields
            if not all([username_valid, email_valid, password_valid]):
                st.error("Please fix the validation errors above")
                return
            
            # Check if username already exists
            existing_users = get_users(token)
            if any(user["username"] == username for user in existing_users):
                st.error("Username already exists")
                return
            
            user_data = {
                "username": username,
                "email": email,
                "password": password,
                "role": role
            }
            
            if create_user(token, user_data):
                # Clear form state on success
                st.session_state.form_state = {
                    "username": "",
                    "email": "",
                    "password": "",
                    "role": "annotator"
                }
                st.rerun()

def users_page():
    """Main function to render the users page"""
    st.title("👥 User Management")
    
    # Check admin access
    if not check_admin_access():
        return
    
    # Create tabs for different sections
    tab_list, tab_create = st.tabs(["User List", "Create User"])
    
    with tab_list:
        render_user_list()
    
    with tab_create:
        render_create_user_form() 