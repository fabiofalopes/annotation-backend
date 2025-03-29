import streamlit as st
import pandas as pd
import requests
from typing import Dict, List, Optional
from datetime import datetime, timezone
from st_aggrid import AgGrid, GridOptionsBuilder
import re

# API Configuration
API_BASE_URL = "http://localhost:8000"
USERS_ENDPOINT = f"{API_BASE_URL}/admin/users"
PROJECTS_ENDPOINT = f"{API_BASE_URL}/admin/projects"

# Mock data for testing
MOCK_USERS = [
    {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin",
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": 2,
        "username": "annotator1",
        "email": "annotator1@example.com",
        "role": "annotator",
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": 3,
        "username": "annotator2",
        "email": "annotator2@example.com",
        "role": "annotator",
        "is_active": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
]

# Initialize session state for mock data
if "mock_users" not in st.session_state:
    st.session_state.mock_users = MOCK_USERS.copy()

def get_users(token: str) -> List[Dict]:
    """Get mock users for testing"""
    return st.session_state.mock_users

def create_user(token: str, user_data: Dict) -> bool:
    """Create a new mock user"""
    try:
        new_user = {
            "id": len(st.session_state.mock_users) + 1,
            "username": user_data["username"],
            "email": user_data["email"],
            "role": user_data["role"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        st.session_state.mock_users.append(new_user)
        st.success("User created successfully!")
        return True
    except Exception as e:
        st.error(f"Error creating user: {str(e)}")
        return False

def delete_user(token: str, user_id: int) -> bool:
    """Delete a mock user"""
    try:
        st.session_state.mock_users = [
            user for user in st.session_state.mock_users 
            if user["id"] != user_id
        ]
        st.success("User deleted successfully!")
        return True
    except Exception as e:
        st.error(f"Error deleting user: {str(e)}")
        return False

def get_user_projects(token: str, user_id: int) -> List[Dict]:
    """Fetch projects assigned to a user"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{USERS_ENDPOINT}/{user_id}/projects", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch user projects: {response.text}")
        return []

def assign_user_to_project(token: str, user_id: int, project_id: int) -> bool:
    """Assign a user to a project"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{PROJECTS_ENDPOINT}/{project_id}/users/{user_id}",
        headers=headers
    )
    if response.status_code == 200:
        st.success("User assigned to project successfully!")
        return True
    else:
        st.error(f"Failed to assign user to project: {response.text}")
        return False

def remove_user_from_project(token: str, user_id: int, project_id: int) -> bool:
    """Remove a user from a project"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"{PROJECTS_ENDPOINT}/{project_id}/users/{user_id}",
        headers=headers
    )
    if response.status_code == 204:
        st.success("User removed from project successfully!")
        return True
    else:
        st.error(f"Failed to remove user from project: {response.text}")
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

def validate_email_format(email: str) -> tuple[bool, str]:
    """Validate email format and check for existing users"""
    if not email:
        return False, "Email is required"
    if not validate_email(email):
        return False, "Invalid email format"
    # Check if email already exists in mock data
    if any(user["email"] == email for user in st.session_state.mock_users):
        return False, "Email already registered"
    return True, ""

def render_user_list():
    """Render the user list with AG Grid"""
    st.subheader("👥 Users")
    
    # Fetch users
    users = get_users("mock_token")
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
                
                # Project Management Section
                st.divider()
                st.write("**Project Management**")
                
                # Mock projects for testing
                if "mock_projects" not in st.session_state:
                    st.session_state.mock_projects = [
                        {"id": 1, "name": "Project A"},
                        {"id": 2, "name": "Project B"},
                        {"id": 3, "name": "Project C"}
                    ]
                
                # Mock user-project assignments
                if "user_projects" not in st.session_state:
                    st.session_state.user_projects = {}
                
                user_id = user['id']
                if user_id not in st.session_state.user_projects:
                    st.session_state.user_projects[user_id] = []
                
                # Display assigned projects
                st.write("Assigned Projects:")
                assigned_projects = st.session_state.user_projects.get(user_id, [])
                if assigned_projects:
                    for project in assigned_projects:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"• {project['name']}")
                        with col2:
                            if st.button("Remove", key=f"remove_{user_id}_{project['id']}"):
                                st.session_state.user_projects[user_id].remove(project)
                                st.success(f"Removed from {project['name']}")
                                st.rerun()
                else:
                    st.write("*No projects assigned*")
                
                # Add to project
                available_projects = [
                    p for p in st.session_state.mock_projects 
                    if p not in assigned_projects
                ]
                
                if available_projects:
                    st.write("Add to Project:")
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        selected_project = st.selectbox(
                            "Select Project",
                            options=available_projects,
                            format_func=lambda x: x['name'],
                            key=f"project_select_{user_id}",
                            label_visibility="collapsed"
                        )
                    with col2:
                        if st.button("Add", key=f"add_{user_id}"):
                            st.session_state.user_projects[user_id].append(selected_project)
                            st.success(f"Added to {selected_project['name']}")
                            st.rerun()
                
                # Delete user section
                st.divider()
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("🗑️ Delete User", type="secondary"):
                        if delete_user("mock_token", user['id']):
                            # Clean up user projects
                            if user['id'] in st.session_state.user_projects:
                                del st.session_state.user_projects[user['id']]
                            st.rerun()

def render_create_user_form():
    """Render the create user form with validation"""
    st.subheader("➕ Create New User")
    
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
        email_valid, email_error = validate_email_format(email)
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
            if any(user["username"] == username for user in st.session_state.mock_users):
                st.error("Username already exists")
                return
            
            user_data = {
                "username": username,
                "email": email,
                "password": password,
                "role": role
            }
            
            if create_user("mock_token", user_data):
                # Clear form state on success
                st.session_state.form_state = {
                    "username": "",
                    "email": "",
                    "password": "",
                    "role": "annotator"
                }
                st.rerun()

def main():
    """Main function to render the users page"""
    st.title("👥 User Management Testing")
    
    # Create tabs for different sections
    tab_list, tab_create = st.tabs(["User List", "Create User"])
    
    with tab_list:
        render_user_list()
    
    with tab_create:
        render_create_user_form()

if __name__ == "__main__":
    main() 