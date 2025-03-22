import streamlit as st
import pandas as pd
from admin_ui.utils.ui_components import display_data_table, confirm_dialog, notification

# Get admin instance
admin = st.session_state.admin

# Page title
st.title("Project Management")

# Create Project Section
with st.container():
    st.subheader("Create New Project")

    # Initialize form key counter
    if "project_form_counter" not in st.session_state:
        st.session_state.project_form_counter = 0
    st.session_state.project_form_counter += 1
    form_key = f"create_project_form_{st.session_state.project_form_counter}"

    with st.form(key=form_key):
        cols = st.columns([2, 2, 2])
        
        # Initialize form values in session state if not present
        if "projects_new_project_form" not in st.session_state:
            st.session_state.projects_new_project_form = {
                "name": "",
                "type": "chat_disentanglement",
                "description": ""
            }
        
        with cols[0]:
            new_project_name = st.text_input(
                "Project Name",
                value=st.session_state.projects_new_project_form["name"],
                key=f"projects_new_project_name_{st.session_state.project_form_counter}",
                placeholder="Enter project name"
            )
        with cols[1]:
            new_project_type = st.selectbox(
                "Project Type",
                ["chat_disentanglement", "document_annotation"],
                index=0 if st.session_state.projects_new_project_form["type"] == "chat_disentanglement" else 1,
                key=f"projects_new_project_type_{st.session_state.project_form_counter}"
            )
        with cols[2]:
            new_project_desc = st.text_area(
                "Description",
                value=st.session_state.projects_new_project_form["description"],
                key=f"projects_new_project_desc_{st.session_state.project_form_counter}",
                placeholder="Project description (optional)"
            )
        
        # Use form_submit_button instead of button
        create_button = st.form_submit_button("Create Project")
        
        if create_button:
            if not new_project_name:
                st.error("Project name is required")
            else:
                try:
                    project = admin.create_project(
                        new_project_name, new_project_type, new_project_desc
                    )
                    st.success(f"Project {project['name']} created successfully!")
                    # Reset form by updating the form state
                    st.session_state.projects_new_project_form = {
                        "name": "",
                        "type": "chat_disentanglement",
                        "description": ""
                    }
                    # Refresh projects list
                    st.session_state.projects = admin.list_projects()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating project: {e}")

st.divider()

# Projects List with Quick Actions
st.subheader("Projects")
refresh_col, spacer = st.columns([1, 5])
with refresh_col:
    if st.button("🔄 Refresh", key=f"refresh_projects_button_{st.session_state.project_form_counter}"):
        st.session_state.projects = admin.list_projects()

# Get projects data
if "projects" not in st.session_state:
    st.session_state.projects = admin.list_projects()

if st.session_state.projects:
    # Display each project as a card with actions
    for project in st.session_state.projects:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"### {project['name']}")
                st.markdown(f"**Type:** {project['type']} | **ID:** {project['id']}")
                description = project.get('description', 'No description')
                st.caption(description)
            
            with col2:
                # Manage Users Button
                if st.button("👥 Users", key=f"users_{project['id']}_{st.session_state.project_form_counter}", type="secondary"):
                    st.session_state.selected_project = project
                    st.session_state.show_project_users = project['id']
                    
            with col3:
                # Delete Project
                if st.button("🗑️ Delete", key=f"delete_project_{project['id']}_{st.session_state.project_form_counter}", type="secondary"):
                    confirm_key = f"confirm_delete_project_{project['id']}"
                    st.session_state[confirm_key] = True
            
            # Show confirmation dialog if delete button was clicked
            confirm_key = f"confirm_delete_project_{project['id']}"
            if confirm_key in st.session_state and st.session_state[confirm_key]:
                with st.container():
                    st.warning(f"Are you sure you want to delete project **{project['name']}**?")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Yes, Delete", key=f"confirm_project_{project['id']}_{st.session_state.project_form_counter}", type="primary"):
                            try:
                                admin.delete_project(project['id'])
                                st.success(f"Project {project['name']} deleted successfully!")
                                st.session_state.projects = admin.list_projects()
                                st.session_state[confirm_key] = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    
                    with col2:
                        if st.button("Cancel", key=f"cancel_project_{project['id']}_{st.session_state.project_form_counter}", type="secondary"):
                            st.session_state[confirm_key] = False
                            st.rerun()
            
            # Show user management if button was clicked
            if hasattr(st.session_state, 'show_project_users') and st.session_state.show_project_users == project['id']:
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
                                    if st.button("Remove", key=f"remove_user_{project['id']}_{user['id']}_{st.session_state.project_form_counter}_{user_idx}", type="secondary"):
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
                                key=f"add_user_{project['id']}_{st.session_state.project_form_counter}"
                            )
                            
                            if st.button("Add User", key=f"add_user_button_{project['id']}_{st.session_state.project_form_counter}"):
                                try:
                                    admin.add_user_to_project(project['id'], user_id)
                                    st.success(f"User added to project successfully!")
                                    # Force refresh of project details and user list
                                    st.session_state.projects = admin.list_projects()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error adding user: {e}")
                        else:
                            st.info("All users are already added to this project.")
                    
                    except Exception as e:
                        st.error(f"Error loading project details: {e}")
                    
                    if st.button("Close", key=f"close_users_{project['id']}_{st.session_state.project_form_counter}"):
                        st.session_state.show_project_users = None
                        st.rerun()
            
            st.divider()
else:
    st.info("No projects found. Create one using the form above.") 