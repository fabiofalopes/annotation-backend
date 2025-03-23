import streamlit as st
import pandas as pd
import traceback
import json
import requests
import uuid
from admin_ui.utils.ui_components import display_data_table, confirm_dialog, notification
from admin_ui.api_client import AnnoBackendAdmin

def show_projects_view():
    admin = st.session_state.get("admin")
    # Check if the user is logged in (admin object exists)
    if admin is None:
        st.error("Please log in to access the Projects page.")
        st.stop()  # Stop execution here

    # Page title
    st.title("Project Management")

    # Debug info in sidebar (keep this for now)
    with st.sidebar:
        st.write("Debug Info:")
        st.write(f"API URL: {admin.base_url if admin else 'Not set'}")
        st.write(f"Token present: {'Yes' if admin and admin.token else 'No'}")
        st.write(f"Headers: {admin.headers if admin else 'Not set'}")

    # Create Project Section
    with st.container():
        st.subheader("Create New Project")

        # Simplified form key
        with st.form(key="create_project_form"):
            cols = st.columns([2, 2, 2])

            with cols[0]:
                new_project_name = st.text_input("Project Name", placeholder="Enter project name")
            with cols[1]:
                new_project_type = st.selectbox(
                    "Project Type",
                    ["chat_disentanglement", "document_annotation"],
                    index=0
                )
            with cols[2]:
                new_project_desc = st.text_area("Description", placeholder="Project description (optional)")

            create_button = st.form_submit_button("Create Project")

            if create_button:
                if not new_project_name:
                    st.error("Project name is required")
                else:
                    try:
                        # Direct API call through admin instance
                        project = admin.create_project(
                            name=new_project_name.strip(),
                            project_type=new_project_type.strip(),
                            description=new_project_desc.strip() if new_project_desc else None
                        )

                        if project:
                            st.success(f"Project {project['name']} created successfully!")
                            # Refresh projects list - simpler now
                            if "projects" in st.session_state:
                                del st.session_state["projects"]
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error creating project: {str(e)}")

    st.divider()

    # Projects List with Quick Actions
    st.subheader("Projects")
    if st.button("🔄 Refresh"): # Simplified refresh
        if "projects" in st.session_state:
            del st.session_state["projects"]
        st.rerun()

    # Get projects data - simpler
    projects = st.session_state.get("projects") or admin.list_projects()
    st.session_state["projects"] = projects


    if projects:
        # Display each project as a card with actions
        for project in projects:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"### {project['name']}")
                    st.markdown(f"**Type:** {project['type']} | **ID:** {project['id']}")
                    description = project.get('description', 'No description')
                    st.caption(description)

                with col2:
                    # Manage Users Button
                    if st.button("👥 Users", key=f"users_{project['id']}", type="secondary"):
                        st.session_state.selected_project = project
                        st.session_state.show_project_users = project['id']
                        st.rerun()

                with col3:
                    # Delete Project
                    if st.button("🗑️ Delete", key=f"delete_project_{project['id']}", type="secondary"):
                        st.session_state.confirm_delete_project = project['id'] # Store just the ID
                        st.rerun()

                # Show confirmation dialog if delete button was clicked
                if st.session_state.get("confirm_delete_project") == project['id']:
                    with st.container():
                        st.warning(f"Are you sure you want to delete project **{project['name']}**?")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Yes, Delete", key=f"confirm_project_{project['id']}", type="primary"):
                                try:
                                    admin.delete_project(project['id'])
                                    st.success(f"Project {project['name']} deleted successfully!")
                                    if "projects" in st.session_state:
                                        del st.session_state["projects"]
                                    if "confirm_delete_project" in st.session_state:
                                        del st.session_state["confirm_delete_project"]
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")

                        with col2:
                            if st.button("Cancel", key=f"cancel_project_{project['id']}", type="secondary"):
                                if "confirm_delete_project" in st.session_state:
                                    del st.session_state["confirm_delete_project"]
                                st.rerun()

                # Show user management if button was clicked
                if st.session_state.get("show_project_users") == project['id']:
                    with st.container():
                        st.markdown(f"#### Manage Users for {project['name']}")

                        # Get project users and refresh user list
                        try:
                            project_details = admin.get_project(project['id'])
                            project_users = project_details.get('users', [])

                            # Always refresh the user list when showing the management section
                            st.session_state.all_users = admin.list_users()

                            # Display current project users
                            if project_users:
                                st.markdown("**Current Users:**")
                                for user_idx, user in enumerate(project_users):
                                    cols = st.columns([3, 1])
                                    with cols[0]:
                                        st.write(f"{user['username']} ({user['role']})")
                                    with cols[1]:
                                        if st.button("Remove", key=f"remove_user_{project['id']}_{user['id']}_{user_idx}", type="secondary"):
                                            try:
                                                admin.remove_user_from_project(project['id'], user['id'])
                                                st.success(f"User {user['username']} removed from project!")
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"Error removing user: {e}")
                            else:
                                st.info("No users assigned to this project.")

                            # Add user to project form
                            st.markdown("**Add User to Project:**")

                            # Filter out users already in the project
                            available_users = [
                                user for user in st.session_state.all_users
                                if user['id'] not in [pu['id'] for pu in project_users]
                            ]

                            if available_users:
                                user_options = {user['id']: f"{user['username']} ({user['role']})" for user in available_users}
                                user_id = st.selectbox(
                                    "Select User",
                                    options=list(user_options.keys()),
                                    format_func=lambda x: user_options[x],
                                    key=f"add_user_{project['id']}"
                                )

                                if st.button("Add User", key=f"add_user_button_{project['id']}"):
                                    try:
                                        admin.add_user_to_project(project['id'], user_id)
                                        st.success(f"User added to project successfully!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error adding user: {e}")
                            else:
                                st.info("All users are already added to this project.")

                        except Exception as e:
                            st.error(f"Error loading project details: {e}")

                        if st.button("Close", key=f"close_users_{project['id']}"):
                            if "show_project_users" in st.session_state:
                                del st.session_state["show_project_users"]
                            st.rerun()

                st.divider()
    else:
        st.info("No projects found. Create one using the form above.") 