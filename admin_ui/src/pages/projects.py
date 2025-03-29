import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import time
import json
from typing import Dict, List, Optional

from api.projects import (
    list_projects, create_project, get_project_details,
    delete_project, add_user_to_project, remove_user_from_project,
    list_project_containers, create_container, delete_container
)
from api.client import show_notification
from config.settings import PROJECT_TYPES, CONTAINER_TYPES

def render_project_details(project_id: int):
    """Render detailed project view with all related information"""
    # Get project details from API
    details = get_project_details(st.session_state.token, project_id)
    
    if not details:
        st.error("Failed to fetch project details")
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
    st.markdown(details.get("description", "No description available"))
    
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
                    if delete_project(st.session_state.token, details["id"]):
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
                if add_user_to_project(st.session_state.token, project_id, user_id):
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
                            if remove_user_from_project(st.session_state.token, project_id, user['id']):
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
                CONTAINER_TYPES
            )
            container_schema = st.text_area("JSON Schema (optional)")
            
            submit = st.form_submit_button("Create Container")
            if submit and container_name:
                schema = None
                if container_schema:
                    try:
                        schema = json.loads(container_schema)
                    except json.JSONDecodeError:
                        show_notification("Invalid JSON schema", "error")
                        return
                
                if create_container(st.session_state.token, project_id, container_name, container_type, schema):
                    show_notification("Container created successfully!", "success")
                    st.rerun()
        
        # List Containers
        st.markdown("### Current Containers")
        containers = list_project_containers(st.session_state.token, project_id)
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
                            if delete_container(st.session_state.token, container['id']):
                                show_notification("Container deleted successfully!", "success")
                                st.rerun()
                    st.markdown("---")
        else:
            st.info("No containers in this project")

def render_project_list():
    """Render the project list using AG Grid"""
    # Fetch projects from API
    projects = list_projects(st.session_state.token)
    
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
            ["All Types"] + PROJECT_TYPES
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
        render_project_details(selected_project["id"])

def render_create_project():
    """Render the create project form"""
    st.subheader("Create New Project")
    
    with st.form("create_project"):
        name = st.text_input("Project Name")
        description = st.text_area("Description")
        project_type = st.selectbox("Project Type", PROJECT_TYPES)
        
        submitted = st.form_submit_button("Create Project")
        
        if submitted:
            if not name:
                st.error("Project name is required")
                return
                
            # Create project via API
            if create_project(st.session_state.token, name, description, project_type):
                st.success("Project created successfully!")
                st.rerun()

def render_projects_page():
    """Main function to render the projects page"""
    st.title("Project Management")
    
    # Create tabs for list and create
    tab1, tab2 = st.tabs(["📋 Project List", "➕ Create Project"])
    
    with tab1:
        render_project_list()
        
    with tab2:
        render_create_project() 