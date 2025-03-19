import streamlit as st
import pandas as pd
from admin_ui.components.data_display import display_data_table, create_expander_section

def render_projects_page():
    """Render the projects management page"""
    st.title("Project Management")
    
    # Project List
    with create_expander_section("Project List", expanded=True):
        if st.button("Refresh Projects", key="refresh_projects_button"):
            st.session_state.projects = st.session_state.admin.list_projects()
        
        if "projects" not in st.session_state:
            st.session_state.projects = st.session_state.admin.list_projects()
        
        if st.session_state.projects:
            projects_data = [
                {
                    "ID": project["id"],
                    "Name": project["name"],
                    "Type": project["type"],
                    "Description": project.get("description", "")
                }
                for project in st.session_state.projects
            ]
            display_data_table(projects_data,
                             columns=["ID", "Name", "Type", "Description"])
    
    # Create Project
    with create_expander_section("Create Project"):
        new_project_name = st.text_input("Project Name", key="new_project_name")
        new_project_type = st.text_input("Project Type", 
                                       value="chat_disentanglement",
                                       key="new_project_type")
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
    with create_expander_section("Project Details"):
        project_id = st.number_input("Project ID", min_value=1, step=1, 
                                   key="get_project_id")
        if st.button("Get Project", key="get_project_button"):
            try:
                project = st.session_state.admin.get_project(project_id)
                st.json(project)
            except Exception as e:
                st.error(f"Error getting project: {e}")
    
    # Manage Project Users
    with create_expander_section("Manage Project Users"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Add User to Project")
            add_project_id = st.number_input("Project ID", min_value=1, step=1,
                                           key="add_project_id")
            add_user_id = st.number_input("User ID", min_value=1, step=1,
                                        key="add_user_id")
            
            if st.button("Add User", key="add_user_to_project_button"):
                try:
                    st.session_state.admin.add_user_to_project(add_project_id, 
                                                             add_user_id)
                    st.success(f"User {add_user_id} added to project {add_project_id}!")
                except Exception as e:
                    st.error(f"Error adding user to project: {e}")
        
        with col2:
            st.subheader("Remove User from Project")
            remove_project_id = st.number_input("Project ID", min_value=1, step=1,
                                              key="remove_project_id")
            remove_user_id = st.number_input("User ID", min_value=1, step=1,
                                           key="remove_user_id")
            
            if st.button("Remove User", key="remove_user_from_project_button"):
                try:
                    st.session_state.admin.remove_user_from_project(remove_project_id,
                                                                  remove_user_id)
                    st.success(f"User {remove_user_id} removed from project {remove_project_id}!")
                except Exception as e:
                    st.error(f"Error removing user from project: {e}")
    
    # Delete Project
    with create_expander_section("Delete Project"):
        delete_project_id = st.number_input("Project ID to Delete", min_value=1,
                                          step=1, key="delete_project_id")
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