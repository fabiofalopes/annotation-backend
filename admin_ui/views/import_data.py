"""
Import Data view module for the Admin UI.
"""
import streamlit as st
from typing import Dict, List, Optional, Any
import pandas as pd
import tempfile
import os
import json
import time

from admin_ui.utils.ui_components import (
    notification,
    loading_spinner
)
from admin_ui.utils.schema_manager import SchemaManager

def suggest_column_mapping(df: pd.DataFrame, project_type: str) -> Dict[str, str]:
    """Suggest column mappings based on common field names.
    
    Args:
        df: The DataFrame containing the data
        project_type: The type of project
        
    Returns:
        Dict mapping our field names to CSV column names
    """
    # Get schema information
    schema = SchemaManager.get_schema_for_type(project_type)
    field_info = SchemaManager.get_field_info(schema)
    
    # Use SchemaManager to suggest mappings
    return SchemaManager.suggest_mapping(list(df.columns), field_info)

def validate_file_upload(
    uploaded_file,
    project_type: str,
    column_mapping: Dict[str, str]
) -> Optional[pd.DataFrame]:
    """Validate the uploaded file and return its contents as a DataFrame.
    
    Args:
        uploaded_file: The uploaded file from st.file_uploader
        project_type: The type of project
        column_mapping: Mapping from our field names to CSV column names
        
    Returns:
        Optional[pd.DataFrame]: The validated DataFrame or None if validation fails
    """
    if not uploaded_file:
        return None
        
    try:
        # Determine file type from extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension == 'jsonl':
            df = pd.read_json(uploaded_file, lines=True)
        else:
            notification("Unsupported file format. Please upload a CSV or JSONL file.", "error")
            return None
            
        # For chat disentanglement, we have specific field requirements
        if project_type == "chat_disentanglement":
            required_fields = ["turn_id", "user_id", "turn_text"]
            missing_required = [field for field in required_fields if field not in column_mapping]
            if missing_required:
                notification(
                    f"Missing mappings for required fields: {', '.join(missing_required)}",
                    "error"
                )
                return None
        else:
            # For other project types, use SchemaManager
            schema = SchemaManager.get_schema_for_type(project_type)
            field_info = SchemaManager.get_field_info(schema)
            missing_required = SchemaManager.validate_mapping(column_mapping, field_info)
            if missing_required:
                notification(
                    f"Missing mappings for required fields: {', '.join(missing_required)}",
                    "error"
                )
                return None
            
        # Check that all mapped columns exist
        missing_columns = [col for col in column_mapping.values() if col not in df.columns]
        if missing_columns:
            notification(
                f"Mapped columns not found in file: {', '.join(missing_columns)}",
                "error"
            )
            return None
            
        # Create a new DataFrame with mapped columns
        mapped_df = pd.DataFrame()
        for our_field, csv_field in column_mapping.items():
            mapped_df[our_field] = df[csv_field]
            
        return mapped_df
        
    except Exception as e:
        notification(f"Error reading file: {str(e)}", "error")
        return None

def show_column_mapping_ui(df: pd.DataFrame, project_type: str) -> Dict[str, str]:
    """Show the column mapping interface.
    
    Args:
        df: The DataFrame containing the data
        project_type: The type of project
        
    Returns:
        Dict mapping our field names to CSV column names
    """
    st.write("### Column Mapping")
    st.write(
        "Map the columns from your file to the required fields. "
        "We've attempted to automatically map common column names."
    )
    
    # For chat disentanglement, we have specific field requirements
    if project_type == "chat_disentanglement":
        field_info = {
            "turn_id": {
                "name": "Turn ID",
                "required": True,
                "description": "Unique identifier for each turn"
            },
            "user_id": {
                "name": "User ID",
                "required": True,
                "description": "ID of the user who sent the message"
            },
            "turn_text": {
                "name": "Message Content",
                "required": True,
                "description": "The message content"
            },
            "reply_to_turn": {
                "name": "Reply To",
                "required": False,
                "description": "ID of the turn this message replies to"
            },
            "thread": {
                "name": "Thread",
                "required": False,
                "description": "Optional thread identifier"
            }
        }
    else:
        # For other project types, use SchemaManager
        schema = SchemaManager.get_schema_for_type(project_type)
        field_info = SchemaManager.get_field_info(schema)
    
    # Get suggested mapping
    suggested_mapping = SchemaManager.suggest_mapping(list(df.columns), field_info)
    
    # Show mapping interface
    mapping = {}
    for field_name, info in field_info.items():
        col1, col2 = st.columns([2, 3])
        with col1:
            st.write(f"**{info['name'] if isinstance(info, dict) else info.name}**")
            if info.get('required', False) if isinstance(info, dict) else info.required:
                st.write("(Required)")
            st.write(f"_{info['description'] if isinstance(info, dict) else info.description}_")
        with col2:
            mapping[field_name] = st.selectbox(
                f"Map to column for {field_name}",
                options=[""] + list(df.columns),
                index=0 if field_name not in suggested_mapping else list(df.columns).index(suggested_mapping[field_name]) + 1,
                key=f"map_{field_name}"
            )
            
    # Remove empty mappings
    return {k: v for k, v in mapping.items() if v}

def show_import_data_view() -> None:
    """Render the import data view."""
    st.title("📥 Import Data")
    
    try:
        # Get list of projects
        projects = st.session_state.admin.list_projects()
        if not projects:
            st.warning("No projects found. Please create a project first.")
            return
            
        # Project selection
        project_options = {
            p["id"]: f"{p['name']} ({p['type']})"
            for p in projects
        }
        
        selected_project_id = st.selectbox(
            "Select Project",
            options=list(project_options.keys()),
            format_func=lambda x: project_options[x]
        )
        
        # Get selected project details
        selected_project = next(
            (p for p in projects if p["id"] == selected_project_id),
            None
        )
        
        if selected_project:
            st.write(
                f"**Project Type:** {selected_project['type']}\n\n"
                f"**Description:** {selected_project.get('description', 'No description')}"
            )
            
            # Container name input
            container_name = st.text_input(
                "Container Name",
                help="Name for the new container that will hold the imported data"
            )
            
            # File upload section
            st.write("### Upload Data")
            st.write(
                "Upload a CSV or JSONL file containing the data to import. "
                "You'll be able to map the columns to the required fields after uploading."
            )
                
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=["csv", "jsonl"],
                help="Upload a CSV or JSONL file"
            )
            
            if uploaded_file:
                # Read the file first to show preview and mapping
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:  # jsonl
                        df = pd.read_json(uploaded_file, lines=True)
                        
                    # Show data preview
                    st.write("### Data Preview")
                    st.dataframe(
                        df.head(),
                        use_container_width=True
                    )
                    
                    # Show column mapping interface
                    column_mapping = show_column_mapping_ui(df, selected_project["type"])
                    
                    if container_name and column_mapping:
                        # Validate with mapping
                        uploaded_file.seek(0)  # Reset file pointer
                        mapped_df = validate_file_upload(
                            uploaded_file,
                            selected_project["type"],
                            column_mapping
                        )
                        
                        if mapped_df is not None:
                            # Show mapped data preview
                            st.write("### Mapped Data Preview")
                            st.dataframe(
                                mapped_df.head(),
                                use_container_width=True
                            )
                            
                            # Import button
                            if st.button("Import Data"):
                                try:
                                    loading_spinner("Importing data...")
                                    
                                    # Save mapped data to a temporary file
                                    with tempfile.NamedTemporaryFile(
                                        mode='w',
                                        suffix='.csv',
                                        delete=False
                                    ) as tmp_file:
                                        mapped_df.to_csv(tmp_file.name, index=False)
                                        
                                        # Import the data based on project type
                                        if selected_project["type"] == "chat_disentanglement":
                                            # For chat data, use import_chat_room
                                            result = st.session_state.admin.import_chat_room(
                                                project_id=selected_project_id,
                                                file=tmp_file.name,
                                                name=container_name,
                                                metadata_columns=json.dumps(column_mapping)
                                            )
                                            
                                            # Show import progress
                                            if result:
                                                st.write("### Import Progress")
                                                st.write(f"Import ID: {result['id']}")
                                                st.write(f"Status: {result['status']}")
                                                st.write(f"Container ID: {result['container_id']}")
                                                st.write(f"Start Time: {result['start_time']}")
                                                
                                                # Create progress bar
                                                progress_bar = st.progress(0)
                                                status_text = st.empty()
                                                error_text = st.empty()
                                                
                                                # Poll for progress updates
                                                max_retries = 60  # 1 minute timeout
                                                retry_count = 0
                                                
                                                while retry_count < max_retries:
                                                    try:
                                                        progress = st.session_state.admin.get_import_progress(result['id'])
                                                        if progress:
                                                            if progress['total_rows'] > 0:
                                                                percentage = progress['processed_rows'] / progress['total_rows']
                                                                progress_bar.progress(percentage)
                                                                status_text.text(
                                                                    f"Processed {progress['processed_rows']} of {progress['total_rows']} rows"
                                                                )
                                                            
                                                            if progress['errors']:
                                                                error_text.error(
                                                                    f"Errors: {', '.join(progress['errors'])}"
                                                                )
                                                            
                                                            if progress['status'] in ['completed', 'failed']:
                                                                if progress['status'] == 'completed':
                                                                    notification(
                                                                        "Import completed successfully!",
                                                                        "success"
                                                                    )
                                                                else:
                                                                    notification(
                                                                        f"Import failed: {', '.join(progress['errors'])}",
                                                                        "error"
                                                                    )
                                                                break
                                                            
                                                            # Wait before next update
                                                            time.sleep(1)
                                                            retry_count += 1
                                                        else:
                                                            # If we can't get progress, wait a bit and retry
                                                            time.sleep(1)
                                                            retry_count += 1
                                                    except Exception as e:
                                                        error_text.error(f"Error checking progress: {str(e)}")
                                                        time.sleep(1)
                                                        retry_count += 1
                                                
                                                if retry_count >= max_retries:
                                                    notification(
                                                        "Import timed out. Please check the status in the Imports section.",
                                                        "warning"
                                                    )
                                                    
                                        else:
                                            # For document data, we need to implement document import
                                            # This should be implemented in the API first
                                            notification(
                                                "Document import not yet implemented. Please implement in the API first.",
                                                "error"
                                            )
                                            return
                                            
                                    # Clean up temporary file
                                    os.unlink(tmp_file.name)
                                        
                                except Exception as e:
                                    notification(f"Failed to import data: {str(e)}", "error")
                                    
                except Exception as e:
                    notification(f"Error reading file: {str(e)}", "error")
                    
    except Exception as e:
        notification(f"Error: {str(e)}", "error") 