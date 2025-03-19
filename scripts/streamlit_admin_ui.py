#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import os
import sys
import json
from typing import Dict, List, Any, Optional
import io
import requests

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
        api_url = os.environ.get('ANNO_API_URL')
        admin = AnnoBackendAdmin(base_url=api_url)
        token = admin.login(username, password)
        # After successful login, the admin instance will have the token in its headers
        st.session_state.authenticated = True
        st.session_state.token = token
        st.session_state.admin = admin  # This admin instance now has the proper token in its headers
        return True
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg:
            st.error("Login failed: Invalid username or password")
        elif "Connection" in error_msg:
            st.error(f"Could not connect to the API server at {api_url}. Please check if the server is running.")
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
    
    # Display API URL (but don't allow editing)
    st.sidebar.text(f"API URL: {os.environ.get('ANNO_API_URL')}")
    
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
    
    # Container List with Type Filter
    with st.expander("Container List", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            filter_project_id = st.number_input("Filter by Project ID (0 for all)", min_value=0, step=1, key="filter_project_id")
        with col2:
            filter_type = st.selectbox(
                "Filter by Type",
                ["All", "chat_rooms", "documents"],
                key="filter_container_type"
            )
        
        if st.button("Refresh Containers", key="refresh_containers_button"):
            try:
                containers = st.session_state.admin.list_containers(
                    project_id=filter_project_id if filter_project_id > 0 else None
                )
                if filter_type != "All":
                    containers = [c for c in containers if c["type"] == filter_type]
                st.session_state.containers = containers
            except Exception as e:
                st.error(f"Error listing containers: {e}")
                st.session_state.containers = []
        
        if "containers" not in st.session_state:
            try:
                containers = st.session_state.admin.list_containers(
                    project_id=filter_project_id if filter_project_id > 0 else None
                )
                if filter_type != "All":
                    containers = [c for c in containers if c["type"] == filter_type]
                st.session_state.containers = containers
            except Exception as e:
                st.error(f"Error listing containers: {e}")
                st.session_state.containers = []
        
        if st.session_state.containers:
            # Convert to DataFrame for better display
            containers_df = pd.DataFrame([
                {
                    "ID": container["id"],
                    "Name": container["name"],
                    "Type": container["type"],
                    "Project ID": container["project_id"],
                    "Items Count": container.get("items_count", "N/A")
                }
                for container in st.session_state.containers
            ])
            st.dataframe(containers_df, use_container_width=True)
            
            # Add quick view buttons for each container
            st.write("Quick Actions:")
            for container in st.session_state.containers:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"Container #{container['id']}: {container['name']}")
                with col2:
                    if st.button("View", key=f"view_container_{container['id']}"):
                        st.session_state.view_container_id = container['id']
                        st.rerun()
        else:
            st.info("No containers found. Create one or adjust filters.")
    
    # View Selected Container
    if hasattr(st.session_state, 'view_container_id') and st.session_state.view_container_id:
        try:
            container = st.session_state.admin.get_container(st.session_state.view_container_id)
            
            # Container Header
            st.header(f"Container: {container['name']}")
            st.write(f"Type: {container['type']} | Project ID: {container['project_id']}")
            
            # Container Actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Close View", key="close_container_view"):
                    st.session_state.view_container_id = None
                    st.rerun()
            with col2:
                if container["type"] == "chat_rooms":
                    if st.button("Import More Data", key="import_more_data"):
                        st.session_state.current_page = "import"
                        st.session_state.pre_selected_container = container['id']
                        st.rerun()
            
            # Display Data Items
            if "items" in container and container["items"]:
                item_count = len(container["items"])
                st.write(f"Total Data Items: {item_count}")
                
                # Chat Room specific view
                if container["type"] == "chat_rooms":
                    # Data display options
                    view_type = st.radio(
                        "View Type",
                        ["Table View", "Chat View", "Thread View"],
                        horizontal=True
                    )
                    
                    # Prepare data
                    messages = []
                    for item in container["items"]:
                        metadata = item.get("item_metadata", {})
                        msg = {
                            "ID": item["id"],
                            "Turn ID": metadata.get("turn_id", ""),
                            "User": metadata.get("user_id", ""),
                            "Message": item["content"],
                            "Reply To": metadata.get("reply_to", ""),
                            "Thread": metadata.get("thread_id", "") or next(
                                (a["data"]["thread_id"] for a in item.get("annotations", []) 
                                if a["type"] == "thread"),
                                ""
                            )
                        }
                        messages.append(msg)
                    
                    if view_type == "Table View":
                        # Sort messages by Turn ID if possible
                        try:
                            messages = sorted(messages, key=lambda x: int(x["Turn ID"]) if x["Turn ID"].isdigit() else float('inf'))
                        except:
                            pass  # Keep original order if sorting fails
                        st.dataframe(pd.DataFrame(messages), use_container_width=True)
                    
                    elif view_type == "Chat View":
                        # Group messages by thread first
                        thread_msgs = {}
                        for msg in messages:
                            thread_id = msg["Thread"] or "main"
                            if thread_id not in thread_msgs:
                                thread_msgs[thread_id] = []
                            thread_msgs[thread_id].append(msg)
                        
                        # Display each thread
                        for thread_id, thread_messages in thread_msgs.items():
                            if thread_id != "main":
                                st.write(f"🧵 Thread: {thread_id}")
                            
                            # Sort messages within thread by Turn ID if possible
                            try:
                                thread_messages = sorted(thread_messages, key=lambda x: int(x["Turn ID"]) if x["Turn ID"].isdigit() else float('inf'))
                            except:
                                pass
                            
                            for msg in thread_messages:
                                with st.chat_message(name=msg["User"]):
                                    header = f"**{msg['User']}** (Turn {msg['Turn ID']})"
                                    st.write(header)
                                    st.write(msg["Message"])
                                    
                                    # Show reply info if available
                                    if msg["Reply To"] and msg["Reply To"] != "nan":
                                        st.caption(f"↩️ Reply to Turn {msg['Reply To']}")
                    
                    else:  # Thread View
                        # Group messages by thread
                        threads = {}
                        unthreaded = []
                        for msg in messages:
                            if msg["Thread"]:
                                if msg["Thread"] not in threads:
                                    threads[msg["Thread"]] = []
                                threads[msg["Thread"]].append(msg)
                            else:
                                unthreaded.append(msg)
                        
                        # Sort messages within each thread by Turn ID
                        for thread_id in threads:
                            try:
                                threads[thread_id] = sorted(threads[thread_id], 
                                    key=lambda x: int(x["Turn ID"]) if x["Turn ID"].isdigit() else float('inf'))
                            except:
                                pass
                        
                        try:
                            unthreaded = sorted(unthreaded,
                                key=lambda x: int(x["Turn ID"]) if x["Turn ID"].isdigit() else float('inf'))
                        except:
                            pass
                        
                        # Display threads
                        st.write("### Conversation Threads")
                        for thread_id, thread_msgs in threads.items():
                            with st.expander(f"Thread {thread_id} ({len(thread_msgs)} messages)", expanded=True):
                                for msg in thread_msgs:
                                    with st.chat_message(name=msg["User"]):
                                        st.write(f"**{msg['User']}** (Turn {msg['Turn ID']})")
                                        st.write(msg["Message"])
                                        if msg["Reply To"] and msg["Reply To"] != "nan":
                                            st.caption(f"↩️ Reply to Turn {msg['Reply To']}")
                        
                        if unthreaded:
                            with st.expander(f"Unthreaded Messages ({len(unthreaded)})", expanded=True):
                                for msg in unthreaded:
                                    with st.chat_message(name=msg["User"]):
                                        st.write(f"**{msg['User']}** (Turn {msg['Turn ID']})")
                                        st.write(msg["Message"])
                                        if msg["Reply To"] and msg["Reply To"] != "nan":
                                            st.caption(f"↩️ Reply to Turn {msg['Reply To']}")
                else:
                    # Generic data item display
                    items_df = pd.DataFrame([
                        {
                            "ID": item["id"],
                            "Content": item["content"],
                            "Metadata": json.dumps(item.get("item_metadata", {}))
                        }
                        for item in container["items"]
                    ])
                    st.dataframe(items_df, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading container: {str(e)}")
            st.session_state.view_container_id = None

# Data import page
def import_page():
    st.title("Data Import")
    
    # Import Chat Room
    with st.expander("Import Chat Room", expanded=True):
        # Project selection
        if "projects" not in st.session_state:
            try:
                st.session_state.projects = st.session_state.admin.list_projects()
            except Exception as e:
                st.error(f"Error loading projects: {e}")
                st.session_state.projects = []
        
        # Filter projects by type
        project_types = list(set(p["type"] for p in st.session_state.projects))
        selected_type = st.selectbox(
            "Select Project Type",
            project_types,
            index=project_types.index("chat_disentanglement") if "chat_disentanglement" in project_types else 0
        )
        
        projects = [
            (p["id"], f"{p['name']} (ID: {p['id']})") 
            for p in st.session_state.projects 
            if p["type"] == selected_type
        ]
        
        if not projects:
            st.warning(f"No {selected_type} projects found. Please create one first.")
            if st.button("Go to Projects"):
                st.session_state.current_page = "projects"
                st.rerun()
            return
        
        project_id = st.selectbox(
            "Select Project",
            [p[0] for p in projects],
            format_func=lambda x: next(p[1] for p in projects if p[0] == x)
        )
        
        # Container selection
        try:
            containers = st.session_state.admin.list_containers(project_id)
            type_containers = [c for c in containers if c["type"] == "chat_rooms"]
        except Exception as e:
            st.error(f"Error loading containers: {e}")
            type_containers = []
        
        container_options = ["Create New Container"] + [
            f"{c['name']} (ID: {c['id']})" for c in type_containers
        ]
        
        # Pre-select container if coming from container view
        preselected_index = 0
        if hasattr(st.session_state, 'pre_selected_container'):
            for i, c in enumerate(type_containers):
                if c['id'] == st.session_state.pre_selected_container:
                    preselected_index = i + 1  # +1 because of "Create New" option
                    break
        
        selected_container = st.selectbox(
            "Select Container",
            container_options,
            index=preselected_index
        )
        
        container_id = None
        if selected_container != "Create New Container":
            container_id = int(selected_container.split("ID: ")[1].rstrip(")"))
        
        if container_id is None:
            room_name = st.text_input("Chat Room Name")
        
        # File upload and validation
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            try:
                # Display a preview of the CSV
                df = pd.read_csv(uploaded_file)
                st.write("Preview of uploaded data:")
                st.dataframe(df.head())
                
                # Define required columns for chat rooms
                required_columns = {
                    'turn_id': ['turn_id', 'turn id', 'turnid', 'turn', 'message_id', 'msg_id', 'id'],
                    'user_id': ['user_id', 'user id', 'userid', 'user', 'speaker', 'speaker_id', 'author'],
                    'turn_text': ['turn_text', 'text', 'content', 'message', 'turn_content', 'msg_text', 'message_text'],
                    'reply_to_turn': ['reply_to_turn', 'reply_to', 'replyto', 'in_reply_to', 'parent_id', 'reply']
                }
                
                # Optional columns
                optional_columns = {
                    'thread': ['thread', 'thread_id', 'conversation', 'topic', 'thread_number', 'thread_idx']
                }
                
                # Auto-detect columns based on exact or fuzzy matches
                detected_columns = {}
                
                # Prioritize exact matches first
                for target_col, variations in {**required_columns, **optional_columns}.items():
                    # First try exact matches
                    exact_match = next((col for col in df.columns if col.lower() in [v.lower() for v in variations]), None)
                    if exact_match:
                        detected_columns[target_col] = exact_match
                        continue
                    
                    # Then try partial/fuzzy matches
                    for col in df.columns:
                        col_lower = col.lower()
                        # Check if any variation is a substring of the column name or vice versa
                        for variation in variations:
                            variation_lower = variation.lower()
                            if variation_lower in col_lower or col_lower in variation_lower:
                                # For fuzzy matches, check that this column wasn't already assigned to another target
                                if col not in detected_columns.values():
                                    detected_columns[target_col] = col
                                    break
                        if target_col in detected_columns:
                            break
                
                # Log detected columns for debugging
                st.write("### Auto-detected Column Mapping")
                if detected_columns:
                    detected_df = pd.DataFrame({
                        "Target Field": list(detected_columns.keys()),
                        "CSV Column": list(detected_columns.values())
                    })
                    st.dataframe(detected_df, use_container_width=True)
                else:
                    st.warning("No columns could be automatically mapped. Please select them manually below.")
                
                # Display column mapping interface with auto-detected defaults
                st.write("### Column Mapping")
                st.write("Map your CSV columns to required fields:")
                
                column_mapping = {}
                mapped_source_columns = []  # Track which source columns are already mapped
                
                # Process required columns first
                for col, variations in required_columns.items():
                    default_index = 0  # Default to empty selection
                    
                    # If we detected this column, set the default index
                    if col in detected_columns:
                        detected_col = detected_columns[col]
                        try:
                            default_index = df.columns.tolist().index(detected_col) + 1  # +1 because we added empty string
                        except ValueError:
                            default_index = 0
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**{col}** (Required)")
                    with col2:
                        mapped_col = st.selectbox(
                            f"Select column for {col}:",
                            [""] + df.columns.tolist(),
                            index=default_index,
                            key=f"select_{col}"
                        )
                        if mapped_col:
                            column_mapping[col] = mapped_col
                            mapped_source_columns.append(mapped_col)
                
                # Process optional columns
                for col, variations in optional_columns.items():
                    default_index = 0  # Default to empty selection
                    
                    # If we detected this column, set the default index
                    if col in detected_columns:
                        detected_col = detected_columns[col]
                        try:
                            default_index = df.columns.tolist().index(detected_col) + 1  # +1 because we added empty string
                        except ValueError:
                            default_index = 0
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**{col}** (Optional)")
                    with col2:
                        mapped_col = st.selectbox(
                            f"Select column for {col}:",
                            [""] + df.columns.tolist(),
                            index=default_index,
                            key=f"select_{col}"
                        )
                        if mapped_col:  # Only add if a column was selected
                            column_mapping[col] = mapped_col
                            mapped_source_columns.append(mapped_col)
                
                # Summary of mapping
                st.write("### Mapping Summary")
                mapping_summary = []
                for target_col, source_col in column_mapping.items():
                    if source_col:
                        target_variations = required_columns.get(target_col) or optional_columns.get(target_col)
                        mapping_summary.append({
                            "CSV Column": source_col,
                            "Maps To": f"{target_col} ({', '.join(target_variations[:2])}...)"
                        })
                
                if mapping_summary:
                    st.table(pd.DataFrame(mapping_summary))
                
                # Validate required columns
                missing_cols = [col for col in required_columns.keys() if col not in column_mapping or not column_mapping[col]]
                if missing_cols:
                    st.error(f"Missing required columns: {', '.join(missing_cols)}")
                else:
                    # Check for duplicate mappings
                    source_cols = list(column_mapping.values())
                    duplicates = [col for col in source_cols if source_cols.count(col) > 1]
                    if duplicates:
                        st.error(f"Column '{duplicates[0]}' is mapped to multiple target fields. Each CSV column should only be mapped once.")
                    else:
                        # Create mapped dataframe
                        if st.button("Preview Mapped Data"):
                            # Create a new dataframe with the correct mappings
                            mapped_df = pd.DataFrame()
                            
                            # For each target field, copy the data from the source column
                            for target_col, source_col in column_mapping.items():
                                if source_col and source_col in df.columns:
                                    mapped_df[target_col] = df[source_col].copy()
                            
                            st.write("### Preview of Mapped Data")
                            st.dataframe(mapped_df.head())
                            
                            # Save both the original data and the mapping for later use
                            st.session_state.original_df = df.copy()
                            st.session_state.column_mapping = column_mapping
                            st.session_state.mapped_df = mapped_df
                            st.session_state.ready_to_import = True
                        
                        # Only show import button if data is mapped and previewed
                        if hasattr(st.session_state, 'ready_to_import') and st.session_state.ready_to_import:
                            if st.button("Import Data", key="import_mapped_data"):
                                try:
                                    # Save mapped data temporarily
                                    temp_file = "temp_upload.csv"
                                    st.session_state.mapped_df.to_csv(temp_file, index=False)
                                    
                                    # Show progress
                                    progress_bar = st.progress(0)
                                    status_text = st.empty()
                                    
                                    status_text.text("Starting import...")
                                    progress_bar.progress(25)
                                    
                                    status_text.text("Uploading to server...")
                                    progress_bar.progress(50)
                                    
                                    # Prepare metadata columns for API
                                    metadata_columns = {}
                                    for target_field, source_col in column_mapping.items():
                                        if source_col:  # Only include non-empty mappings
                                            metadata_columns[target_field] = source_col
                                    
                                    # Debug information
                                    st.write("### Debug Information:")
                                    st.write(f"Project ID: {project_id}")
                                    st.write(f"Container ID: {container_id}")
                                    st.write(f"Room Name: {room_name if container_id is None else None}")
                                    st.write("Original Columns:")
                                    st.dataframe(st.session_state.original_df.head(2))
                                    st.write("Mapped Columns:")
                                    st.dataframe(st.session_state.mapped_df.head(2))
                                    st.write("Column Mapping:")
                                    st.json(metadata_columns)
                                    
                                    # Debug API connection
                                    try:
                                        # Test API connection
                                        api_url = st.session_state.admin.base_url
                                        st.write(f"API URL: {api_url}")
                                        
                                        # Debug auth information
                                        st.write("### Auth Debug:")
                                        st.write(f"Token: {st.session_state.token}")
                                        st.write(f"Headers: {st.session_state.admin.headers}")
                                        
                                        # Test with a simple GET request to verify connectivity
                                        test_response = requests.get(
                                            f"{api_url}/chat-disentanglement/projects/{project_id}",
                                            headers=st.session_state.admin.headers  # Include auth token
                                        )
                                        st.write(f"API Test Response: {test_response.status_code}")
                                        if test_response.status_code != 200:
                                            st.error(f"API connection error: {test_response.text}")
                                        
                                        # Full endpoint URL being called
                                        endpoint_url = f"{api_url}/chat-disentanglement/projects/{project_id}/rooms/import"
                                        st.write(f"Import Endpoint URL: {endpoint_url}")
                                    except Exception as e:
                                        st.error(f"API connection test error: {str(e)}")
                                    
                                    # Verify project exists
                                    try:
                                        project = st.session_state.admin.get_project(project_id)
                                        if not project:
                                            st.error(f"Project with ID {project_id} not found")
                                            return
                                    except Exception as e:
                                        st.error(f"Error verifying project: {str(e)}")
                                        return
                                    
                                    result = st.session_state.admin.import_chat_room(
                                        project_id,
                                        temp_file,
                                        room_name if container_id is None else None,
                                        container_id=container_id,
                                        metadata_columns=metadata_columns
                                    )
                                    
                                    progress_bar.progress(75)
                                    status_text.text("Processing data...")
                            
                                    # Clean up
                                    if os.path.exists(temp_file):
                                        os.remove(temp_file)
                                    
                                    progress_bar.progress(100)
                                    status_text.text("Import complete!")
                                    
                                    # Success message with details
                                    container_id = result.get('container_id')
                                    st.success(f"Data imported successfully to container #{container_id}!")
                                    
                                    # Display mapping information if available
                                    if 'mapped_columns' in result:
                                        st.write("### Column Mappings Used:")
                                        mapping_df = pd.DataFrame([
                                            {"Field": k, "CSV Column": v} 
                                            for k, v in result['mapped_columns'].items() 
                                            if v is not None
                                        ])
                                        st.table(mapping_df)
                                    
                                    # Display import statistics
                                    st.write(f"**Items imported:** {result.get('items_imported', 0)}")
                                    
                                    # Clear the import state
                                    st.session_state.ready_to_import = False
                                    if hasattr(st.session_state, 'mapped_df'):
                                        del st.session_state.mapped_df
                                    
                                    # View imported data
                                    if st.button("View Imported Data"):
                                        st.session_state.current_page = "containers"
                                        st.session_state.view_container_id = container_id
                                        if hasattr(st.session_state, 'pre_selected_container'):
                                            del st.session_state.pre_selected_container
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error importing data: {str(e)}")
                                    st.error("Full error details:")
                                    st.code(str(e))
                                    # Clear the error state
                                    st.session_state.ready_to_import = False
                                    if hasattr(st.session_state, 'mapped_df'):
                                        del st.session_state.mapped_df
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")
                st.error("Please ensure your CSV file is properly formatted and not corrupted.")

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