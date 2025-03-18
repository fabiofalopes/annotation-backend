#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import os
import sys
import json
from typing import Dict, List, Any, Optional

# Import from the admin script
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
from admin import AnnoBackendAdmin

# Set page configuration
st.set_page_config(
    page_title="Annotation Backend Admin",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "token" not in st.session_state:
    st.session_state.token = None
if "admin" not in st.session_state:
    st.session_state.admin = None

# Function to handle login
def login(username: str, password: str):
    try:
        admin = AnnoBackendAdmin(base_url=st.session_state.api_url)
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
            st.error(f"Could not connect to the API server at {st.session_state.api_url}. Please check if the server is running.")
        else:
            st.error(f"Login failed: {e}")
        return False

# Function to refresh data
def refresh_data():
    try:
        if hasattr(st.session_state, 'current_page'):
            if st.session_state.current_page == "users":
                st.session_state.users = st.session_state.admin.list_users()
            elif st.session_state.current_page == "projects":
                st.session_state.projects = st.session_state.admin.list_projects()
            elif st.session_state.current_page == "containers":
                st.session_state.containers = st.session_state.admin.list_containers()
    except Exception as e:
        st.error(f"Error refreshing data: {e}")

# Sidebar navigation
def sidebar():
    st.sidebar.title("Navigation")
    
    # API URL configuration
    api_url = st.sidebar.text_input(
        "API URL",
        value=os.environ.get("ANNO_API_URL", "http://localhost:8000"),
        key="api_url"
    )
    
    # If not authenticated, show login form
    if not st.session_state.authenticated:
        st.sidebar.header("Login")
        username = st.sidebar.text_input("Username", value="admin", key="login_username")
        password = st.sidebar.text_input("Password", type="password", key="login_password")
        if st.sidebar.button("Login", key="login_button"):
            login(username, password)
            if st.session_state.authenticated:
                st.sidebar.success("Logged in successfully!")
                st.rerun()
    else:
        st.sidebar.success("Authenticated ✓")
        if st.sidebar.button("Logout", key="logout_button"):
            st.session_state.authenticated = False
            st.session_state.token = None
            st.session_state.admin = None
            st.rerun()
        
        # Navigation buttons
        st.sidebar.header("Manage")
        if st.sidebar.button("Users", key="nav_users_button"):
            st.session_state.current_page = "users"
            refresh_data()
            st.rerun()
        if st.sidebar.button("Projects", key="nav_projects_button"):
            st.session_state.current_page = "projects"
            refresh_data()
            st.rerun()
        if st.sidebar.button("Data Containers", key="nav_containers_button"):
            st.session_state.current_page = "containers"
            refresh_data()
            st.rerun()
        if st.sidebar.button("Import Data", key="nav_import_button"):
            st.session_state.current_page = "import"
            st.rerun()

# User management page
def users_page():
    st.title("User Management")
    
    # User List
    with st.expander("User List", expanded=True):
        if st.button("Refresh Users", key="refresh_users_button"):
            st.session_state.users = st.session_state.admin.list_users()
        
        if "users" not in st.session_state:
            st.session_state.users = st.session_state.admin.list_users()
        
        if st.session_state.users:
            # Convert to DataFrame for better display
            users_df = pd.DataFrame([
                {
                    "ID": user["id"],
                    "Username": user["username"],
                    "Email": user["email"],
                    "Role": user["role"],
                    "Active": "Yes" if user["is_active"] else "No"
                }
                for user in st.session_state.users
            ])
            st.dataframe(users_df)
    
    # Create User
    with st.expander("Create User"):
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Username", key="new_username")
            new_email = st.text_input("Email", key="new_email")
        with col2:
            new_password = st.text_input("Password", type="password", help="Password must be at least 8 characters long", key="new_password")
            new_role = st.selectbox("Role", ["annotator", "admin"], key="new_role")
        
        if st.button("Create User", key="create_user_button"):
            if not new_username or not new_email or not new_password:
                st.error("Please fill in all fields")
            elif len(new_password) < 8:
                st.error("Password must be at least 8 characters long")
            else:
                try:
                    user = st.session_state.admin.create_user(
                        new_username, new_email, new_password, new_role
                    )
                    st.success(f"User {user['username']} created successfully!")
                    st.session_state.users = st.session_state.admin.list_users()
                except Exception as e:
                    st.error(f"Error creating user: {e}")
    
    # Get User Details
    with st.expander("User Details"):
        user_id = st.number_input("User ID", min_value=1, step=1, key="get_user_id")
        if st.button("Get User", key="get_user_button"):
            try:
                user = st.session_state.admin.get_user(user_id)
                st.json(user)
            except Exception as e:
                st.error(f"Error getting user: {e}")
    
    # Delete User
    with st.expander("Delete User"):
        delete_user_id = st.number_input("User ID to Delete", min_value=1, step=1, key="delete_user_id")
        confirm_delete = st.checkbox("Confirm deletion", key="confirm_user_deletion")
        if st.button("Delete User", key="delete_user_button"):
            if confirm_delete:
                try:
                    st.session_state.admin.delete_user(delete_user_id)
                    st.success(f"User {delete_user_id} deleted successfully!")
                    st.session_state.users = st.session_state.admin.list_users()
                except Exception as e:
                    st.error(f"Error deleting user: {e}")
            else:
                st.warning("Please confirm deletion")

# Project management page
def projects_page():
    st.title("Project Management")
    
    # Project List
    with st.expander("Project List", expanded=True):
        if st.button("Refresh Projects", key="refresh_projects_button"):
            st.session_state.projects = st.session_state.admin.list_projects()
        
        if "projects" not in st.session_state:
            st.session_state.projects = st.session_state.admin.list_projects()
        
        if st.session_state.projects:
            # Convert to DataFrame for better display
            projects_df = pd.DataFrame([
                {
                    "ID": project["id"],
                    "Name": project["name"],
                    "Type": project["type"],
                    "Description": project.get("description", "")
                }
                for project in st.session_state.projects
            ])
            st.dataframe(projects_df)
    
    # Create Project
    with st.expander("Create Project"):
        new_project_name = st.text_input("Project Name", key="new_project_name")
        new_project_type = st.text_input("Project Type", value="chat_disentanglement", key="new_project_type")
        new_project_desc = st.text_area("Description", key="new_project_desc")
        
        if st.button("Create Project", key="create_project_button"):
            if not new_project_name:
                st.error("Project name is required")
            elif not new_project_type:
                st.error("Project type is required")
            else:
                try:
                    project = st.session_state.admin.create_project(
                        new_project_name, new_project_type, new_project_desc
                    )
                    st.success(f"Project {project['name']} created successfully!")
                    st.session_state.projects = st.session_state.admin.list_projects()
                except Exception as e:
                    st.error(f"Error creating project: {e}")
    
    # Get Project Details
    with st.expander("Project Details"):
        project_id = st.number_input("Project ID", min_value=1, step=1, key="get_project_id")
        if st.button("Get Project", key="get_project_button"):
            try:
                project = st.session_state.admin.get_project(project_id)
                st.json(project)
            except Exception as e:
                st.error(f"Error getting project: {e}")
    
    # Manage Project Users
    with st.expander("Manage Project Users"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Add User to Project")
            add_project_id = st.number_input("Project ID", min_value=1, step=1, key="add_project_id")
            add_user_id = st.number_input("User ID", min_value=1, step=1, key="add_user_id")
            
            if st.button("Add User", key="add_user_to_project_button"):
                try:
                    st.session_state.admin.add_user_to_project(add_project_id, add_user_id)
                    st.success(f"User {add_user_id} added to project {add_project_id}!")
                except Exception as e:
                    st.error(f"Error adding user to project: {e}")
        
        with col2:
            st.subheader("Remove User from Project")
            remove_project_id = st.number_input("Project ID", min_value=1, step=1, key="remove_project_id")
            remove_user_id = st.number_input("User ID", min_value=1, step=1, key="remove_user_id")
            
            if st.button("Remove User", key="remove_user_from_project_button"):
                try:
                    st.session_state.admin.remove_user_from_project(remove_project_id, remove_user_id)
                    st.success(f"User {remove_user_id} removed from project {remove_project_id}!")
                except Exception as e:
                    st.error(f"Error removing user from project: {e}")
    
    # Delete Project
    with st.expander("Delete Project"):
        delete_project_id = st.number_input("Project ID to Delete", min_value=1, step=1, key="delete_project_id")
        confirm_delete = st.checkbox("Confirm deletion", key="confirm_project_deletion")
        if st.button("Delete Project", key="delete_project_button"):
            if confirm_delete:
                try:
                    st.session_state.admin.delete_project(delete_project_id)
                    st.success(f"Project {delete_project_id} deleted successfully!")
                    st.session_state.projects = st.session_state.admin.list_projects()
                except Exception as e:
                    st.error(f"Error deleting project: {e}")
            else:
                st.warning("Please confirm deletion")

# Data container management page
def containers_page():
    st.title("Data Container Management")
    
    # Container List
    with st.expander("Container List", expanded=True):
        filter_project_id = st.number_input("Filter by Project ID (0 for all)", min_value=0, step=1, key="filter_project_id")
        
        if st.button("Refresh Containers", key="refresh_containers_button"):
            if filter_project_id > 0:
                st.session_state.containers = st.session_state.admin.list_containers(filter_project_id)
            else:
                st.session_state.containers = st.session_state.admin.list_containers()
        
        if "containers" not in st.session_state:
            if filter_project_id > 0:
                st.session_state.containers = st.session_state.admin.list_containers(filter_project_id)
            else:
                st.session_state.containers = st.session_state.admin.list_containers()
        
        if st.session_state.containers:
            # Convert to DataFrame for better display
            containers_df = pd.DataFrame([
                {
                    "ID": container["id"],
                    "Name": container["name"],
                    "Type": container["type"],
                    "Project ID": container["project_id"]
                }
                for container in st.session_state.containers
            ])
            st.dataframe(containers_df)
    
    # Create Container
    with st.expander("Create Container"):
        new_container_name = st.text_input("Container Name", key="new_container_name")
        new_container_type = st.text_input("Container Type", value="chat_room", key="new_container_type")
        new_container_project = st.number_input("Project ID", min_value=1, step=1, key="new_container_project_id")
        
        schema_option = st.radio("Schema", ["Default", "Custom"], key="schema_option")
        json_schema = None
        
        if schema_option == "Custom":
            schema_json = st.text_area("JSON Schema", value="{}", key="custom_schema_json")
            try:
                json_schema = json.loads(schema_json)
            except:
                st.error("Invalid JSON schema")
        
        if st.button("Create Container", key="create_container_button"):
            if not new_container_name:
                st.error("Container name is required")
            elif not new_container_type:
                st.error("Container type is required")
            elif new_container_project < 1:
                st.error("Valid project ID is required")
            elif schema_option == "Custom" and json_schema is None:
                st.error("Please provide a valid JSON schema")
            else:
                try:
                    container = st.session_state.admin.create_container(
                        new_container_name, new_container_type, new_container_project, json_schema
                    )
                    st.success(f"Container {container['name']} created successfully!")
                    st.session_state.containers = st.session_state.admin.list_containers()
                except Exception as e:
                    st.error(f"Error creating container: {e}")
    
    # Get Container Details
    with st.expander("Container Details"):
        container_id = st.number_input("Container ID", min_value=1, step=1, key="get_container_id")
        if st.button("Get Container", key="get_container_button"):
            try:
                container = st.session_state.admin.get_container(container_id)
                st.json(container)
            except Exception as e:
                st.error(f"Error getting container: {e}")

# Data import page
def import_page():
    st.title("Data Import")
    
    # Import Chat Room
    with st.expander("Import Chat Room", expanded=True):
        project_id = st.number_input("Project ID", min_value=1, step=1)
        room_name = st.text_input("Chat Room Name (optional)")
        
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            try:
                # Display a preview of the CSV
                df = pd.read_csv(uploaded_file)
                st.write("Preview:")
                st.dataframe(df.head())
                
                # Check for required columns
                required_columns = ['turn_id', 'user_id', 'content', 'reply_to']
                missing_cols = [col for col in required_columns if col not in df.columns]
                
                # Flag to track if validation passes
                validation_passed = len(missing_cols) == 0
                
                if missing_cols:
                    st.warning(f"Missing required columns: {', '.join(missing_cols)}")
                    
                    # Try to map columns
                    st.write("Available columns:")
                    st.write(df.columns.tolist())
                    
                    mapping = {}
                    for req_col in missing_cols:
                        col_map = st.selectbox(
                            f"Map '{req_col}' to:",
                            [""] + df.columns.tolist(),
                            key=f"select_{req_col}"
                        )
                        if col_map:
                            mapping[col_map] = req_col
                    
                    if mapping and st.button("Apply Mapping", key="apply_mapping_button"):
                        df = df.rename(columns=mapping)
                        st.write("After mapping:")
                        st.dataframe(df.head())
                        
                        # Check if all required columns exist after mapping
                        still_missing = [col for col in required_columns if col not in df.columns]
                        if still_missing:
                            st.error(f"Still missing columns: {', '.join(still_missing)}")
                            validation_passed = False
                        else:
                            st.success("All required columns are now available!")
                            validation_passed = True
                            
                            # Update the uploaded file with mapped columns
                            temp_file = "temp_mapping.csv"
                            df.to_csv(temp_file, index=False)
                            with open(temp_file, 'rb') as f:
                                uploaded_file = st.file_uploader("Mapped CSV file", type="csv", key="mapped_file")
                                if uploaded_file is None:  # If the user hasn't uploaded yet, use our temp file
                                    import io
                                    uploaded_file = io.BytesIO(f.read())
                            if os.path.exists(temp_file):
                                os.remove(temp_file)
                
                if validation_passed and st.button("Import Data", key="import_data_button"):
                    if project_id < 1:
                        st.error("Please provide a valid project ID")
                    else:
                        try:
                            # Save uploaded file temporarily
                            temp_file = "temp_upload.csv"
                            with open(temp_file, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            # Import using the admin script
                            result = st.session_state.admin.import_chat_room(
                                project_id, temp_file, room_name
                            )
                            
                            # Clean up
                            if os.path.exists(temp_file):
                                os.remove(temp_file)
                            
                            st.success("Data imported successfully!")
                        except Exception as e:
                            st.error(f"Error importing data: {e}")
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")

# Main app
def main():
    # Render sidebar
    sidebar()
    
    # Show appropriate page based on navigation
    if not st.session_state.authenticated:
        st.title("Annotation Backend Admin")
        st.write("Please log in using the sidebar to access the admin interface.")
    else:
        if not hasattr(st.session_state, 'current_page'):
            st.session_state.current_page = "users"
        
        # Render the appropriate page
        if st.session_state.current_page == "users":
            users_page()
        elif st.session_state.current_page == "projects":
            projects_page()
        elif st.session_state.current_page == "containers":
            containers_page()
        elif st.session_state.current_page == "import":
            import_page()

if __name__ == "__main__":
    main() 