import streamlit as st
import pandas as pd
import os
import json
import requests
import time
import uuid
from admin_ui.utils.ui_components import notification, display_data_table, confirm_dialog
from typing import Dict, List, Optional
import tempfile
from pathlib import Path
import traceback
from admin_ui.api_client import AnnoBackendAdmin

def show_import_data_view():
    admin = st.session_state.get("admin")
    # Check if the user is logged in (admin object exists)
    if admin is None:
        st.error("Please log in to access the Import Data page.")
        st.stop()  # Stop execution here

    # Use a request ID approach to track rendering cycles instead of a simple flag
    view_id = "import_data_view"
    if f"current_request_id_{view_id}" not in st.session_state:
        st.session_state[f"current_request_id_{view_id}"] = str(uuid.uuid4())
    if f"rendered_request_id_{view_id}" not in st.session_state:
        st.session_state[f"rendered_request_id_{view_id}"] = None

    # Check if we've already rendered this specific request ID
    current_request_id = st.session_state[f"current_request_id_{view_id}"]
    rendered_request_id = st.session_state[f"rendered_request_id_{view_id}"]

    if current_request_id == rendered_request_id:
        # Generate a new request ID for the next cycle and stop this rendering
        st.session_state[f"current_request_id_{view_id}"] = str(uuid.uuid4())
        st.stop()

    # Mark that we've rendered this request
    st.session_state[f"rendered_request_id_{view_id}"] = current_request_id

    # Page title
    st.title("Import Data")

    # Debug info
    with st.sidebar:
        st.write("Debug Info:")
        st.write(f"API URL: {admin.base_url if admin else 'Not set'}")
        st.write(f"Token present: {'Yes' if admin and admin.token else 'No'}")
        st.write(f"Headers: {admin.headers if admin else 'Not set'}")

    # Get list of projects
    if "import_projects" not in st.session_state:
        try:
            st.session_state.import_projects = admin.list_projects()
        except Exception as e:
            st.error(f"Error fetching projects: {str(e)}")
            st.session_state.import_projects = []

    # Initialize form key counter in session state
    if "import_form_counter" not in st.session_state:
        st.session_state.import_form_counter = 0
    if "import_form_uuid" not in st.session_state:
        st.session_state.import_form_uuid = str(uuid.uuid4())

    # Create a unique form key using both counter and uuid
    form_key = f"import_data_form_{st.session_state.import_form_counter}_{st.session_state.import_form_uuid}"

    with st.form(key=form_key):
        st.subheader("Import Data")
        
        # Project selection
        project_options = {p["id"]: p["name"] for p in st.session_state.import_projects}
        
        # Check if we should pre-select a project
        selected_project_id = None
        if hasattr(st.session_state, 'pre_selected_container') and st.session_state.pre_selected_container:
            # Get the project ID from the container
            try:
                container = admin.get_container(st.session_state.pre_selected_container)
                selected_project_id = container.get('project_id')
            except Exception as e:
                st.error(f"Error fetching container details: {str(e)}")
        
        # Display project dropdown
        if project_options:
            selected_project = st.selectbox(
                "Select Project",
                options=list(project_options.keys()),
                format_func=lambda x: project_options[x],
                index=list(project_options.keys()).index(selected_project_id) if selected_project_id in project_options else 0,
                key=f"import_project_select_{st.session_state.import_form_counter}_{st.session_state.import_form_uuid}"
            )
        else:
            st.error("No projects available. Please create a project first.")
            selected_project = None
        
        # Data import options
        if selected_project:
            # Get the project details to know what type it is
            try:
                project_details = admin.get_project(selected_project)
                project_type = project_details.get('type', 'unknown')
                
                # Different import options based on project type
                if project_type == 'chat_disentanglement':
                    import_type = st.selectbox(
                        "Import Type",
                        ["CSV File", "JSONL File", "Chat History"],
                        key=f"import_type_{st.session_state.import_form_counter}_{st.session_state.import_form_uuid}"
                    )
                    
                    if import_type == "CSV File":
                        uploaded_file = st.file_uploader(
                            "Upload CSV File", 
                            type=["csv"],
                            key=f"import_csv_{st.session_state.import_form_counter}_{st.session_state.import_form_uuid}"
                        )
                        container_name = st.text_input(
                            "Container Name", 
                            value=f"Chat Import {uuid.uuid4().hex[:8]}",
                            key=f"import_container_name_{st.session_state.import_form_counter}_{st.session_state.import_form_uuid}"
                        )
                    
                    elif import_type == "JSONL File":
                        uploaded_file = st.file_uploader(
                            "Upload JSONL File", 
                            type=["jsonl", "json"],
                            key=f"import_jsonl_{st.session_state.import_form_counter}_{st.session_state.import_form_uuid}"
                        )
                        container_name = st.text_input(
                            "Container Name", 
                            value=f"Chat Import {uuid.uuid4().hex[:8]}",
                            key=f"import_container_name_jsonl_{st.session_state.import_form_counter}_{st.session_state.import_form_uuid}"
                        )
                        
                    else:  # Chat History
                        chat_history = st.text_area(
                            "Paste Chat History", 
                            height=300,
                            key=f"import_chat_history_{st.session_state.import_form_counter}_{st.session_state.import_form_uuid}"
                        )
                        container_name = st.text_input(
                            "Container Name", 
                            value=f"Chat Import {uuid.uuid4().hex[:8]}",
                            key=f"import_container_name_text_{st.session_state.import_form_counter}_{st.session_state.import_form_uuid}"
                        )
                        
                elif project_type == 'document_annotation':
                    import_type = st.selectbox(
                "Import Type",
                        ["PDF Document", "Text Document", "JSONL File"],
                        key=f"import_doc_type_{st.session_state.import_form_counter}_{st.session_state.import_form_uuid}"
                    )
                    
                    uploaded_file = st.file_uploader(
                        f"Upload {import_type.split()[0]} File", 
                        type=["pdf", "txt", "jsonl", "json"],
                        key=f"import_doc_{st.session_state.import_form_counter}_{st.session_state.import_form_uuid}"
                    )
                    container_name = st.text_input(
                        "Container Name", 
                        value=f"Document Import {uuid.uuid4().hex[:8]}",
                        key=f"import_container_name_doc_{st.session_state.import_form_counter}_{st.session_state.import_form_uuid}"
                    )
                    
                else:
                    st.error(f"Unsupported project type: {project_type}")
            except Exception as e:
                st.error(f"Error fetching project details: {str(e)}")
        
        # Submit button
        submit_button = st.form_submit_button("Import Data")
        
        if submit_button:
            # Increment the counter after the form is submitted
            st.session_state.import_form_counter += 1
            # Generate a new UUID for the next form
            st.session_state.import_form_uuid = str(uuid.uuid4())
            
            if not selected_project:
                st.error("Please select a project")
            elif project_type == 'chat_disentanglement':
                if import_type == "CSV File" and uploaded_file is not None:
                    try:
                        # Write the file to a temporary location
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name
                        
                        # Call the import API
                        result = admin.import_chat_data(
                            project_id=selected_project,
                            container_name=container_name,
                            file_path=tmp_path,
                            file_type="csv",
                        )
                        
                        # Clean up temp file
                        os.unlink(tmp_path)
                        
                        if result and result.get('success'):
                            st.success(f"Data imported successfully! Container ID: {result.get('container_id')}")
                            # Generate a new request ID to force a re-render on the next cycle
                            st.session_state[f"current_request_id_{view_id}"] = str(uuid.uuid4())
                        else:
                            st.error(f"Import failed: {result.get('message', 'Unknown error')}")
                            
                    except Exception as e:
                        st.error(f"Error importing data: {str(e)}")
                        st.error(traceback.format_exc())
                
                elif import_type == "JSONL File" and uploaded_file is not None:
                    try:
                        # Write the file to a temporary location
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jsonl') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name
                        
                        # Call the import API
                        result = admin.import_chat_data(
                            project_id=selected_project,
                            container_name=container_name,
                            file_path=tmp_path,
                            file_type="jsonl"
                        )
                        
                        # Clean up temp file
                        os.unlink(tmp_path)
                        
                        if result and result.get('success'):
                            st.success(f"Data imported successfully! Container ID: {result.get('container_id')}")
                            # Generate a new request ID to force a re-render on the next cycle
                            st.session_state[f"current_request_id_{view_id}"] = str(uuid.uuid4())
                        else:
                            st.error(f"Import failed: {result.get('message', 'Unknown error')}")
                            
                    except Exception as e:
                        st.error(f"Error importing data: {str(e)}")
                        st.error(traceback.format_exc())
                
                elif import_type == "Chat History" and chat_history:
                    try:
                        # Write the chat history to a temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
                            tmp_file.write(chat_history.encode('utf-8'))
                            tmp_path = tmp_file.name
                        
                        # Call the import API
                        result = admin.import_chat_data(
                            project_id=selected_project,
                            container_name=container_name,
                            file_path=tmp_path,
                            file_type="chat"
                        )
                        
                        # Clean up temp file
                        os.unlink(tmp_path)
                        
                        if result and result.get('success'):
                            st.success(f"Data imported successfully! Container ID: {result.get('container_id')}")
                            # Generate a new request ID to force a re-render on the next cycle
                            st.session_state[f"current_request_id_{view_id}"] = str(uuid.uuid4())
                        else:
                            st.error(f"Import failed: {result.get('message', 'Unknown error')}")

                    except Exception as e:
                        st.error(f"Error importing data: {str(e)}")
                        st.error(traceback.format_exc())
                
                else:
                    st.error("Please provide the required data")
                
            elif project_type == 'document_annotation' and uploaded_file is not None:
                try:
                    # Determine file type suffix
                    suffix_map = {
                        "PDF Document": ".pdf",
                        "Text Document": ".txt",
                        "JSONL File": ".jsonl"
                    }
                    suffix = suffix_map.get(import_type, ".txt")
                    
                    # Write the file to a temporary location
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    # Call the import API
                    result = admin.import_document_data(
                        project_id=selected_project,
                        container_name=container_name,
                        file_path=tmp_path,
                        file_type=suffix[1:]  # Remove the dot
                    )
                    
                    # Clean up temp file
                    os.unlink(tmp_path)
                    
                    if result and result.get('success'):
                        st.success(f"Document imported successfully! Container ID: {result.get('container_id')}")
                        # Generate a new request ID to force a re-render on the next cycle
                        st.session_state[f"current_request_id_{view_id}"] = str(uuid.uuid4())
                    else:
                        st.error(f"Import failed: {result.get('message', 'Unknown error')}")
                    
                except Exception as e:
                    st.error(f"Error importing document: {str(e)}")
                    st.error(traceback.format_exc())
            else:
                st.error("Please provide the required data")

    # Import History Section
    st.divider()
    st.subheader("Recent Imports")

    refresh_col, spacer = st.columns([1, 5])
    with refresh_col:
        if st.button("🔄 Refresh", key="refresh_imports_button"):
            # Let's clear the containers to force a refresh
            st.session_state.pop('containers', None)
            # Generate a new request ID to force a re-render on the next cycle
            st.session_state[f"current_request_id_{view_id}"] = str(uuid.uuid4())
            st.rerun()

    # Get containers data
    if "containers" not in st.session_state:
        try:
            # Get all containers - we'll sort them in memory
            containers = admin.list_containers()
            # Sort by creation time if available
            containers.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            # Take only the 10 most recent
            st.session_state.containers = containers[:10]
        except Exception as e:
            st.error(f"Error listing imports: {str(e)}")
            st.session_state.containers = []

    if st.session_state.containers:
        # Display each container as a card with actions
        for container in st.session_state.containers:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"### {container['name']}")
                    st.markdown(f"**Type:** {container.get('type', 'Unknown')} | **Project ID:** {container.get('project_id', 'Unknown')}")
                    items_count = container.get('items_count', 'Unknown')
                    st.caption(f"Items: {items_count}")
                
                with col2:
                    # View Container Details
                    if st.button("👁️ View", key=f"view_{container['id']}", type="primary"):
                        st.session_state.selected_container = container
                        # Generate a new request ID to force a re-render on the next cycle
                        st.session_state[f"current_request_id_{view_id}"] = str(uuid.uuid4())
                        st.rerun()
                    
                with col3:
                    # Delete Container
                    if st.button("🗑️ Delete", key=f"delete_{container['id']}", type="secondary"):
                        confirm_key = f"confirm_delete_{container['id']}"
                        st.session_state[confirm_key] = True
                        # Generate a new request ID to force a re-render on the next cycle
                        st.session_state[f"current_request_id_{view_id}"] = str(uuid.uuid4())
                        st.rerun()
                
                # Show confirmation dialog if delete button was clicked
                confirm_key = f"confirm_delete_{container['id']}"
                if confirm_key in st.session_state and st.session_state[confirm_key]:
                    with st.container():
                        st.warning(f"Are you sure you want to delete **{container['name']}**?")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Yes, Delete", key=f"confirm_{container['id']}", type="primary"):
                                try:
                                    admin.delete_container(container['id'])
                                    st.success(f"Data {container['name']} deleted successfully!")
                                    # Refresh containers list
                                    containers = admin.list_containers()
                                    st.session_state.containers = containers[:10]
                                    st.session_state[confirm_key] = False
                                    # Generate a new request ID to force a re-render on the next cycle
                                    st.session_state[f"current_request_id_{view_id}"] = str(uuid.uuid4())
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        
                        with col2:
                            if st.button("Cancel", key=f"cancel_{container['id']}", type="secondary"):
                                st.session_state[confirm_key] = False
                                # Generate a new request ID to force a re-render on the next cycle
                                st.session_state[f"current_request_id_{view_id}"] = str(uuid.uuid4())
                                st.rerun()
                
                st.divider()
        
        # Container Details View
        if hasattr(st.session_state, 'selected_container') and st.session_state.selected_container:
            container = st.session_state.selected_container
            
            # Container Header
            st.header(f"Container: {container['name']}")
            st.write(f"Type: {container.get('type', 'Unknown')} | Project ID: {container.get('project_id', 'Unknown')}")
            
            # Container Actions
            if st.button("Close View", key="close_container_view"):
                st.session_state.selected_container = None
                # Generate a new request ID to force a re-render on the next cycle
                st.session_state[f"current_request_id_{view_id}"] = str(uuid.uuid4())
                st.rerun()
            
            # Display Data Items if available
            try:
                container_details = admin.get_container(container['id'])
                if "items" in container_details and container_details["items"]:
                    item_count = len(container_details["items"])
                    st.write(f"Total Data Items: {item_count}")
                    
                    # Basic table display of items
                    items_df = pd.DataFrame([
                        {
                            "ID": item["id"],
                            "Content": item["content"][:100] + "..." if len(item["content"]) > 100 else item["content"],
                            "Type": item.get("type", "Unknown")
                        }
                        for item in container_details["items"]
                    ])
                    st.dataframe(items_df, use_container_width=True)
                    
                    # Offer download option
                    if st.button("Export as JSONL", key=f"export_{container['id']}"):
                        try:
                            # Create JSONL content
                            jsonl_content = "\n".join([json.dumps(item) for item in container_details["items"]])
                            
                            # Create download button
                            st.download_button(
                                label="Download JSONL",
                                data=jsonl_content,
                                file_name=f"{container['name']}_export.jsonl",
                                mime="application/json"
                            )
                        except Exception as e:
                            st.error(f"Error preparing export: {str(e)}")
                else:
                    st.info("No data items available in this container.")
            except Exception as e:
                st.error(f"Error loading container details: {str(e)}")
    else:
            st.info("No imports found. Import some data using the form above.") 