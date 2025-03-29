import streamlit as st
import requests
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
import pandas as pd
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_lottie import st_lottie
import json
import time

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
ADMIN_API_URL = f"{API_BASE_URL}/admin-api"

# Lottie Animations
LOADING_ANIMATION_URL = "https://assets5.lottiefiles.com/packages/lf20_qm8eqzse.json"
SUCCESS_ANIMATION_URL = "https://assets2.lottiefiles.com/packages/lf20_s2lryxtd.json"

def load_lottie_url(url: str) -> Dict:
    """Load lottie animation from URL"""
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

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
    return {"Authorization": f"Bearer {token}"}

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
        
        response.raise_for_status()
        return response.json() if response.content else None
    except requests.exceptions.RequestException as e:
        show_notification(f"API Error: {str(e)}", "error")
        return None

def login(username: str, password: str) -> Optional[str]:
    """Login to get access token"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/token",
            data={"username": username, "password": password}
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        show_notification(f"Login failed: {str(e)}", "error")
        return None

def list_projects(token: str) -> list:
    """List all projects"""
    return api_request("GET", "/projects/", token) or []

def create_project(token: str, name: str, description: str, project_type: str) -> Optional[Dict]:
    """Create a new project"""
    data = {
        "name": name,
        "description": description,
        "type": project_type
    }
    return api_request("POST", "/projects/", token, data)

def get_project_details(token: str, project_id: int) -> Optional[Dict]:
    """Get project details"""
    return api_request("GET", f"/projects/{project_id}", token)

def delete_project(token: str, project_id: int) -> bool:
    """Delete a project"""
    result = api_request("DELETE", f"/projects/{project_id}", token)
    return result is not None

def render_login_page():
    """Render the login page"""
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.title("👋 Welcome Back!")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not username or not password:
                    show_notification("Please enter both username and password", "error")
                else:
                    with st.spinner("Logging in..."):
                        token = login(username, password)
                        if token:
                            st.session_state.token = token
                            st.success("Login successful!")
                            time.sleep(1)  # Give time for success message
                            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def render_project_details(token: str, project_id: int):
    """Render detailed project view with all related information"""
    details = get_project_details(token, project_id)
    if not details:
        return

    # Project Overview
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Project Name:** {details['name']}")
        st.markdown(f"**Type:** {details['type']}")
        st.markdown(f"**Created By:** {details.get('created_by_id', 'N/A')}")
    with col2:
        st.markdown(f"**Created:** {details.get('created_at', 'N/A')}")
        st.markdown(f"**Status:** Active")
        st.markdown(f"**ID:** {details['id']}")
    
    st.markdown("**Description:**")
    st.markdown(details["description"])
    
    # Tabs for different project aspects
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "👥 Users", "📁 Containers"])
    
    # Overview Tab
    with tab1:
        # Project Statistics
        st.subheader("Project Statistics")
        stat1, stat2, stat3 = st.columns(3)
        with stat1:
            st.metric("Total Containers", len(details.get('containers', [])))
        with stat2:
            st.metric("Total Users", len(details.get('users', [])))
        with stat3:
            st.metric("Status", "Active", delta="Up")
        
        # Action Buttons
        st.markdown("---")
        st.subheader("Actions")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🗑️ Delete Project"):
                if st.session_state.get("confirm_delete") != details["id"]:
                    st.session_state.confirm_delete = details["id"]
                    show_notification("Click delete again to confirm", "error")
                else:
                    if delete_project(token, details["id"]):
                        show_notification("Project deleted successfully", "success")
                        st.session_state.pop("confirm_delete", None)
                        time.sleep(1)
                        st.rerun()
    
    # Users Tab
    with tab2:
        st.subheader("Project Users")
        
        # Add User Form
        st.markdown("### Add User to Project")
        with st.form("add_user_form"):
            user_id = st.number_input("User ID", min_value=1, step=1)
            submit = st.form_submit_button("Add User")
            if submit:
                response = api_request(
                    "POST", 
                    f"/projects/{project_id}/users/{user_id}", 
                    token
                )
                if response:
                    show_notification("User added successfully!", "success")
                    st.rerun()
        
        # List Users
        st.markdown("### Current Users")
        if details.get('users'):
            for user in details['users']:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"👤 {user.get('username', 'N/A')} ({user.get('email', 'N/A')})")
                    with col2:
                        if st.button("Remove", key=f"remove_user_{user['id']}"):
                            response = api_request(
                                "DELETE",
                                f"/projects/{project_id}/users/{user['id']}",
                                token
                            )
                            if response:
                                show_notification("User removed successfully!", "success")
                                st.rerun()
        else:
            st.info("No users assigned to this project")
    
    # Containers Tab
    with tab3:
        st.subheader("Data Containers")
        
        # Create Container Form
        st.markdown("### Create New Container")
        with st.form("create_container_form"):
            container_name = st.text_input("Container Name")
            container_type = st.selectbox(
                "Container Type",
                ["dataset", "results", "annotations"]
            )
            container_schema = st.text_area("JSON Schema (optional)")
            
            submit = st.form_submit_button("Create Container")
            if submit and container_name:
                response = api_request(
                    "POST",
                    "/containers/",
                    token,
                    {
                        "name": container_name,
                        "type": container_type,
                        "project_id": project_id,
                        "json_schema": container_schema if container_schema else None
                    }
                )
                if response:
                    show_notification("Container created successfully!", "success")
                    st.rerun()
        
        # List Containers
        st.markdown("### Current Containers")
        containers = api_request("GET", f"/containers/?project_id={project_id}", token)
        if containers:
            for container in containers:
                with st.container():
                    st.markdown(f"#### 📁 {container['name']}")
                    st.write(f"**Type:** {container['type']}")
                    if container.get('json_schema'):
                        with st.container():
                            st.write("**Schema:**")
                            st.json(container['json_schema'])
                    
                    # Container Actions
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("View Items", key=f"view_items_{container['id']}"):
                            st.session_state.selected_container = container['id']
                    with col2:
                        if st.button("Delete", key=f"delete_container_{container['id']}"):
                            # Add delete container functionality
                            pass
                    st.markdown("---")
        else:
            st.info("No containers in this project")

def render_project_list(token: str):
    """Render the project list using AG Grid"""
    projects = list_projects(token)
    if not projects:
        st.info("No projects found. Create your first project!")
        return
    
    # Add search and filter options
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("🔍 Search Projects", "")
    with col2:
        project_type_filter = st.selectbox(
            "Filter by Type",
            ["All Types", "chat_disentanglement", "text_classification", "other"]
        )
    
    # Filter projects based on search and type
    df = pd.DataFrame(projects)
    if search:
        df = df[df['name'].str.contains(search, case=False) | 
                df['description'].str.contains(search, case=False)]
    if project_type_filter != "All Types":
        df = df[df['type'] == project_type_filter]
    
    # Configure grid
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
    gb.configure_column("name", header_name="Project Name")
    gb.configure_column("description", header_name="Description")
    gb.configure_column("type", header_name="Type")
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    
    grid_options = gb.build()
    grid_return = AgGrid(
        df,
        gridOptions=grid_options,
        enable_enterprise_modules=True,
        update_mode="selection_changed",
        height=400,
        theme="streamlit"
    )
    
    selected_rows = grid_return.get("selected_rows", [])
    if isinstance(selected_rows, pd.DataFrame):
        selected_rows = selected_rows.to_dict('records')
    
    if selected_rows and len(selected_rows) > 0:
        selected_project = selected_rows[0]
        st.markdown("---")
        st.subheader("📋 Project Details")
        render_project_details(token, selected_project["id"])

def render_create_project():
    """Render the create project form"""
    st.subheader("Create New Project")
    with st.form("create_project"):
        name = st.text_input("Project Name")
        description = st.text_area("Description")
        project_type = st.selectbox(
            "Project Type",
            ["chat_disentanglement", "text_classification", "other"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Create Project", use_container_width=True)
        with col2:
            clear = st.form_submit_button("Clear Form", use_container_width=True)
        
        if submit:
            if not name:
                show_notification("Project name is required", "error")
            else:
                with st.spinner("Creating project..."):
                    if create_project(st.session_state.token, name, description, project_type):
                        show_notification("Project created successfully!", "success")
                        time.sleep(1)
                        st.rerun()

def main():
    st.set_page_config(
        page_title="Project Management Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    # Initialize session state
    if "token" not in st.session_state:
        st.session_state.token = None
    
    # Login page
    if not st.session_state.token:
        render_login_page()
        return
    
    # Main dashboard
    with st.sidebar:
        selected = option_menu(
            menu_title="Navigation",
            options=["Projects", "Create Project", "Settings"],
            icons=["folder", "plus-square", "gear"],
            menu_icon="cast",
            default_index=0,
        )
        
        # Logout button at bottom of sidebar
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            st.session_state.token = None
            st.rerun()
    
    # Main content
    if selected == "Projects":
        st.title("📁 Projects")
        render_project_list(st.session_state.token)
    
    elif selected == "Create Project":
        st.title("➕ Create Project")
        render_create_project()
    
    elif selected == "Settings":
        st.title("⚙️ Settings")
        st.info("Settings page coming soon!")

if __name__ == "__main__":
    main() 