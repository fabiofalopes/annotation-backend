"""
Projects view module for the Admin UI.
"""
import streamlit as st
from typing import Dict, List

from admin_ui.utils.ui_components import (
    notification,
    confirm_dialog,
    display_data_table,
    loading_spinner
)

def create_project_form() -> None:
    """Render the create project form."""
    with st.form("create_project_form"):
        st.subheader("Create New Project")
        
        name = st.text_input("Project Name")
        description = st.text_area("Description")
        project_type = st.selectbox(
            "Project Type",
            options=[
                "chat_disentanglement",
                "document_annotation"
            ],
            format_func=lambda x: "Chat Disentanglement" if x == "chat_disentanglement" else "Document Annotation",
            help="Select the type of project"
        )
        
        if st.form_submit_button("Create Project"):
            try:
                loading_spinner("Creating project...")
                st.session_state.admin.create_project(
                    name=name,
                    project_type=project_type,
                    description=description
                )
                notification("Project created successfully!", "success")
                st.rerun()  # Refresh to show the new project
            except Exception as e:
                notification(f"Failed to create project: {str(e)}", "error")

def delete_project(project_id: str) -> None:
    """Delete a project.
    
    Args:
        project_id: The ID of the project to delete
    """
    try:
        st.session_state.admin.delete_project(project_id)
        notification("Project deleted successfully!", "success")
        st.rerun()  # Refresh to remove the deleted project
    except Exception as e:
        notification(f"Failed to delete project: {str(e)}", "error")

def manage_project_users(project_id: str, project_name: str) -> None:
    """Manage users for a project.
    
    Args:
        project_id: The ID of the project
        project_name: The name of the project for display
    """
    st.subheader(f"Manage Users for {project_name}")
    
    try:
        # Get project details and all available users
        project = st.session_state.admin.get_project(project_id)
        all_users = st.session_state.admin.list_users()
        
        # Get project users from project details
        project_users = project.get("users", [])
        project_user_ids = {user["id"] for user in project_users}
        
        # Display available users to add
        available_users = [u for u in all_users if u["id"] not in project_user_ids]
        if available_users:
            user_to_add = st.selectbox(
                "Add User",
                options=[(u["id"], u["username"]) for u in available_users],
                format_func=lambda x: x[1]
            )
            
            if st.button("Add Selected User"):
                try:
                    st.session_state.admin.add_user_to_project(
                        project_id=project_id,
                        user_id=user_to_add[0]
                    )
                    notification(f"Added user {user_to_add[1]} to project!", "success")
                    st.rerun()
                except Exception as e:
                    notification(f"Failed to add user: {str(e)}", "error")
        
        # Display and manage current project users
        if project_users:
            st.subheader("Current Project Users")
            for user in project_users:
                cols = st.columns([3, 1])
                with cols[0]:
                    st.write(f"**{user['username']}** ({user['email']})")
                with cols[1]:
                    if st.button(f"Remove", key=f"remove_{user['id']}"):
                        try:
                            st.session_state.admin.remove_user_from_project(
                                project_id=project_id,
                                user_id=user["id"]
                            )
                            notification(f"Removed {user['username']} from project!", "success")
                            st.rerun()
                        except Exception as e:
                            notification(f"Failed to remove user: {str(e)}", "error")
        else:
            st.info("No users assigned to this project.")
            
    except Exception as e:
        notification(f"Failed to manage project users: {str(e)}", "error")

def format_project_data(projects: List[Dict]) -> List[Dict]:
    """Format project data for display.
    
    Args:
        projects: List of project dictionaries from the API
        
    Returns:
        List of formatted project dictionaries
    """
    formatted_projects = []
    for project in projects:
        formatted_projects.append({
            "ID": project.get("id", "N/A"),
            "Name": project.get("name", "N/A"),
            "Type": project.get("type", "N/A"),
            "Description": project.get("description", "N/A"),
            "Created At": project.get("created_at", "N/A")
        })
    return formatted_projects

def show_projects_view() -> None:
    """Render the projects view."""
    st.title("📁 Project Management")
    
    # Create project form in the sidebar
    with st.sidebar:
        st.markdown("---")
        create_project_form()
    
    try:
        # Fetch and display projects
        projects = st.session_state.admin.list_projects()
        if projects:
            formatted_projects = format_project_data(projects)
            
            # Display projects table
            st.subheader("Current Projects")
            display_data_table(
                data=formatted_projects,
                key="projects_table"
            )
            
            # Project actions
            st.subheader("Project Actions")
            for project in projects:
                st.markdown(f"### {project['name']} ({project['type']})")
                cols = st.columns([2, 1])
                with cols[0]:
                    st.write(f"**Description:** {project.get('description', 'No description')}")
                    st.write(f"**Created:** {project.get('created_at', 'N/A')}")
                with cols[1]:
                    confirm_dialog(
                        title=f"Delete {project['name']}",
                        message=f"Are you sure you want to delete project {project['name']}? This will delete all associated data!",
                        on_confirm=lambda pid=project['id']: delete_project(pid)
                    )
                
                # Project user management section
                st.markdown("---")
                manage_project_users(project['id'], project['name'])
                st.markdown("---")
        else:
            st.info("No projects found.")
            
    except Exception as e:
        notification(f"Failed to load projects: {str(e)}", "error") 