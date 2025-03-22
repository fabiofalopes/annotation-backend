import streamlit as st
import pandas as pd
import os
import json
import requests
import time
from admin_ui.utils.ui_components import notification
from typing import Dict, List, Optional
import tempfile
from pathlib import Path

# Get admin instance
admin = st.session_state.admin

# Page title
st.title("Data Import")

# Project selection
if "projects" not in st.session_state:
    try:
        st.session_state.projects = admin.list_projects()
    except Exception as e:
        st.error(f"Error loading projects: {e}")
        st.session_state.projects = []

# Filter projects by type
if st.session_state.projects:
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
    else:
        project_id = st.selectbox(
            "Select Project",
            [p[0] for p in projects],
            format_func=lambda x: next(p[1] for p in projects if p[0] == x)
        )
        
        # Container selection
        try:
            containers = admin.list_containers(project_id)
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

        # Import type selection
        import_type = st.radio(
            "Import Type",
            ["Single File", "Multiple Files", "Directory"],
            help="Choose how you want to import data"
        )

        if import_type == "Single File":
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
            files_to_process = [uploaded_file] if uploaded_file else []
        
        elif import_type == "Multiple Files":
            uploaded_files = st.file_uploader("Choose CSV files", type="csv", accept_multiple_files=True)
            files_to_process = uploaded_files
        
        else:  # Directory
            uploaded_files = st.file_uploader("Choose CSV files from directory", type="csv", accept_multiple_files=True)
            files_to_process = uploaded_files

        # Initialize session state for file processing
        if 'processed_files' not in st.session_state:
            st.session_state.processed_files = {}
        
        if 'column_mappings' not in st.session_state:
            st.session_state.column_mappings = {}

        if 'import_operations' not in st.session_state:
            st.session_state.import_operations = {}

        # Process files
        if files_to_process:
            st.write("### Files to Process")
            
            # Required columns for chat rooms
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

            # Process each file
            for file_idx, file in enumerate(files_to_process):
                st.write(f"#### File {file_idx + 1}: {file.name}")
                
                # Create three columns for file preview and mapping
                col1, col2 = st.columns([1, 1])
                
                # Read the file
                try:
                    df = pd.read_csv(file)
                    
                    with col1:
                        st.write("Preview:")
                        st.dataframe(df.head())

                    # Auto-detect columns
                    detected_columns = {}
                    
                    # First try exact matches
                    for target_col, variations in {**required_columns, **optional_columns}.items():
                        exact_match = next((col for col in df.columns if col.lower() in [v.lower() for v in variations]), None)
                        if exact_match:
                            detected_columns[target_col] = exact_match
                            continue
                        
                        # Then try partial/fuzzy matches
                        for col in df.columns:
                            col_lower = col.lower()
                            for variation in variations:
                                variation_lower = variation.lower()
                                if variation_lower in col_lower or col_lower in variation_lower:
                                    if col not in detected_columns.values():
                                        detected_columns[target_col] = col
                                        break
                            if target_col in detected_columns:
                                break

                    # Store detected mappings in session state
                    if file.name not in st.session_state.column_mappings:
                        st.session_state.column_mappings[file.name] = detected_columns

                    with col2:
                        st.write("Column Mapping:")
                        mapping_col1, mapping_col2 = st.columns([1, 1])
                        
                        with mapping_col1:
                            st.write("Required Fields")
                            for field in required_columns.keys():
                                st.session_state.column_mappings[file.name][field] = st.selectbox(
                                    f"Map {field}",
                                    [""] + list(df.columns),
                                    index=list(df.columns).index(st.session_state.column_mappings[file.name].get(field, "")) + 1 if st.session_state.column_mappings[file.name].get(field, "") in df.columns else 0,
                                    key=f"{file.name}_{field}"
                                )

                        with mapping_col2:
                            st.write("Optional Fields")
                            for field in optional_columns.keys():
                                st.session_state.column_mappings[file.name][field] = st.selectbox(
                                    f"Map {field}",
                                    [""] + list(df.columns),
                                    index=list(df.columns).index(st.session_state.column_mappings[file.name].get(field, "")) + 1 if st.session_state.column_mappings[file.name].get(field, "") in df.columns else 0,
                                    key=f"{file.name}_{field}"
                                )

                    # Validate mappings
                    missing_required = [
                        field for field in required_columns.keys()
                        if not st.session_state.column_mappings[file.name].get(field)
                    ]

                    if missing_required:
                        st.error(f"Missing required mappings: {', '.join(missing_required)}")
                    else:
                        st.success("All required fields are mapped!")

                    # Store processed dataframe
                    if not missing_required:
                        # Create mapped dataframe
                        mapped_df = pd.DataFrame()
                        for target_col, source_col in st.session_state.column_mappings[file.name].items():
                            if source_col:
                                mapped_df[target_col] = df[source_col].copy()
                        
                        # Store in session state
                        st.session_state.processed_files[file.name] = {
                            'df': mapped_df,
                            'mappings': st.session_state.column_mappings[file.name]
                        }

                except Exception as e:
                    st.error(f"Error processing file {file.name}: {str(e)}")
                    continue

                st.markdown("---")  # Add separator between files

            # Import button
            if st.session_state.processed_files and not any(missing_required):
                if st.button("Import All Files"):
                    progress_container = st.empty()
                    status_text = st.empty()
                    
                    try:
                        # Start bulk import
                        if len(files_to_process) > 1:
                            # Use bulk import endpoint
                            with tempfile.TemporaryDirectory() as temp_dir:
                                temp_files = []
                                for filename, file_data in st.session_state.processed_files.items():
                                    temp_path = os.path.join(temp_dir, filename)
                                    file_data['df'].to_csv(temp_path, index=False)
                                    temp_files.append(("files", open(temp_path, "rb")))

                                # Make bulk import request
                                response = admin.bulk_import_chat_rooms(
                                    project_id=project_id,
                                    files=temp_files,
                                    container_id=container_id,
                                    metadata_columns=json.dumps({
                                        filename: data['mappings']
                                        for filename, data in st.session_state.processed_files.items()
                                    })
                                )

                                # Store import IDs
                                for import_id in response.get('import_ids', []):
                                    st.session_state.import_operations[import_id] = {
                                        'status': 'pending',
                                        'progress': 0
                                    }

                        else:
                            # Use single file import
                            filename = list(st.session_state.processed_files.keys())[0]
                            file_data = st.session_state.processed_files[filename]
                            
                            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
                                file_data['df'].to_csv(temp_file.name, index=False)
                                
                                # Import the file
                                response = admin.import_chat_room(
                                    project_id=project_id,
                                    file=temp_file.name,
                                    name=f"{room_name}_{filename}" if room_name else filename,
                                    container_id=container_id,
                                    metadata_columns=json.dumps(file_data['mappings'])
                                )

                                # Store import ID
                                import_id = response.get('import_id')
                                if import_id:
                                    st.session_state.import_operations[import_id] = {
                                        'status': 'pending',
                                        'progress': 0
                                    }

                        # Monitor import progress
                        while True:
                            all_completed = True
                            total_progress = 0
                            active_imports = 0

                            for import_id in st.session_state.import_operations:
                                try:
                                    progress = admin.get_import_progress(import_id)
                                    st.session_state.import_operations[import_id]['status'] = progress['status']
                                    st.session_state.import_operations[import_id]['progress'] = progress['progress_percentage']
                                    
                                    if progress['status'] not in ['completed', 'failed']:
                                        all_completed = False
                                        active_imports += 1
                                    
                                    total_progress += progress['progress_percentage']
                                    
                                    # Show individual progress
                                    status_text.text(f"Processing {import_id}: {progress['status']} ({progress['progress_percentage']:.1f}%)")
                                    
                                    # Show errors if any
                                    if progress['errors']:
                                        st.error(f"Errors in {import_id}:")
                                        for error in progress['errors']:
                                            st.error(error)
                                
                                except Exception as e:
                                    st.error(f"Error checking progress for {import_id}: {str(e)}")
                            
                            # Update overall progress
                            if st.session_state.import_operations:
                                avg_progress = total_progress / len(st.session_state.import_operations)
                                progress_container.progress(int(avg_progress))
                            
                            if all_completed:
                                break
                            
                            time.sleep(1)  # Wait before next check

                        # Show final status
                        status_text.text("Import complete!")
                        
                        # Clear session state
                        st.session_state.processed_files = {}
                        st.session_state.column_mappings = {}
                        st.session_state.import_operations = {}
                        st.experimental_rerun()

                    except Exception as e:
                        st.error(f"Error during import: {str(e)}")
else:
    st.warning("No projects found. Please create a project first.") 