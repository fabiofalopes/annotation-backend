import streamlit as st
import pandas as pd
import requests
from typing import Dict, List
from datetime import datetime

from utils.api import get_api_url, get_auth_header
from utils.auth import check_admin_access

# API endpoints
USERS_ENDPOINT = f"{get_api_url()}/admin/users"
PROJECTS_ENDPOINT = f"{get_api_url()}/admin/projects"

def get_user_details(token: str, user_id: int) -> Dict:
    """Fetch detailed user information"""
    try:
        response = requests.get(
            f"{USERS_ENDPOINT}/{user_id}",
            headers=get_auth_header(token)
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch user details: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error fetching user details: {str(e)}")
        return None

def get_user_projects(token: str, user_id: int) -> List[Dict]:
    """Fetch projects assigned to a user"""
    try:
        response = requests.get(
            f"{USERS_ENDPOINT}/{user_id}/projects",
            headers=get_auth_header(token)
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch user projects: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error fetching user projects: {str(e)}")
        return []

def get_all_projects(token: str) -> List[Dict]:
    """Fetch all available projects"""
    try:
        response = requests.get(
            PROJECTS_ENDPOINT,
            headers=get_auth_header(token)
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch projects: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error fetching projects: {str(e)}")
        return []

def assign_user_to_project(token: str, user_id: int, project_id: int) -> bool:
    """Assign a user to a project"""
    try:
        response = requests.post(
            f"{PROJECTS_ENDPOINT}/{project_id}/users/{user_id}",
            headers=get_auth_header(token)
        )
        if response.status_code == 200:
            st.success("User assigned to project successfully!")
            return True
        else:
            st.error(f"Failed to assign user to project: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error assigning user to project: {str(e)}")
        return False

def remove_user_from_project(token: str, user_id: int, project_id: int) -> bool:
    """Remove a user from a project"""
    try:
        response = requests.delete(
            f"{PROJECTS_ENDPOINT}/{project_id}/users/{user_id}",
            headers=get_auth_header(token)
        )
        if response.status_code == 204:
            st.success("User removed from project successfully!")
            return True
        else:
            st.error(f"Failed to remove user from project: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error removing user from project: {str(e)}")
        return False

def render_user_details(user_id: int):
    """Render detailed user information and project associations"""
    # Get token from session state
    token = st.session_state.get("token")
    if not token:
        st.error("Please log in first")
        return

    # Fetch user details
    user = get_user_details(token, user_id)
    if not user:
        return

    # Display user information
    st.title(f"👤 {user['username']}")
    
    # Basic Information
    st.subheader("Basic Information")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**ID:**", user['id'])
        st.write("**Username:**", user['username'])
        st.write("**Email:**", user['email'])
    with col2:
        st.write("**Role:**", user['role'])
        st.write("**Status:**", "✅ Active" if user['is_active'] else "❌ Inactive")
        st.write("**Created:**", datetime.fromisoformat(user['created_at']).strftime('%Y-%m-%d %H:%M:%S'))

    # Project Assignments
    st.subheader("Project Assignments")
    
    # Fetch user's projects
    user_projects = get_user_projects(token, user_id)
    
    # Display current project assignments
    if user_projects:
        st.write("**Current Projects:**")
        for project in user_projects:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"• **{project['name']}**")
                if project.get('description'):
                    st.write(f"  {project['description']}")
            with col2:
                if st.button("Remove", key=f"remove_{project['id']}"):
                    if remove_user_from_project(token, user_id, project['id']):
                        st.rerun()
    else:
        st.info("No projects assigned")

    # Add to Project section
    st.write("**Add to Project:**")
    
    # Fetch all projects
    all_projects = get_all_projects(token)
    
    # Filter out projects the user is already assigned to
    available_projects = [
        p for p in all_projects 
        if not any(up['id'] == p['id'] for up in user_projects)
    ]
    
    if available_projects:
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_project = st.selectbox(
                "Select Project",
                options=available_projects,
                format_func=lambda x: x['name'],
                key="project_select"
            )
        with col2:
            if st.button("Add"):
                if assign_user_to_project(token, user_id, selected_project['id']):
                    st.rerun()
    else:
        st.info("No available projects to assign")

def user_details_page():
    """Main function to render the user details page"""
    # Check admin access
    if not check_admin_access():
        return
    
    # Get user ID from query parameters
    query_params = st.experimental_get_query_params()
    user_id = query_params.get("user_id", [None])[0]
    
    if user_id is None:
        st.error("No user ID provided")
        return
    
    try:
        user_id = int(user_id)
        render_user_details(user_id)
    except ValueError:
        st.error("Invalid user ID") 