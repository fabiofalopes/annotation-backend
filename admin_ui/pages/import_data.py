import streamlit as st
import pandas as pd
import os
from admin_ui.components.data_display import create_expander_section

def render_import_page():
    """Render the data import page"""
    st.title("Data Import")
    
    # Import Chat Room
    with create_expander_section("Import Chat Room", expanded=True):
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
                
                # Auto-detect columns
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
                        for variation in variations:
                            variation_lower = variation.lower()
                            if variation_lower in col_lower or col_lower in variation_lower:
                                if col not in detected_columns.values():
                                    detected_columns[target_col] = col
                                    break
                        if target_col in detected_columns:
                            break
                
                # Show detected columns
                st.write("### Auto-detected Column Mapping")
                if detected_columns:
                    detected_df = pd.DataFrame({
                        "Target Field": list(detected_columns.keys()),
                        "CSV Column": list(detected_columns.values())
                    })
                    st.dataframe(detected_df, use_container_width=True)
                else:
                    st.warning("No columns could be automatically mapped. Please select them manually below.")
                
                # Column mapping interface
                st.write("### Column Mapping")
                st.write("Map your CSV columns to required fields:")
                
                column_mapping = {}
                mapped_source_columns = []
                
                # Process required columns first
                for col, variations in required_columns.items():
                    default_index = 0
                    if col in detected_columns:
                        detected_col = detected_columns[col]
                        try:
                            default_index = df.columns.tolist().index(detected_col) + 1
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
                    default_index = 0
                    if col in detected_columns:
                        detected_col = detected_columns[col]
                        try:
                            default_index = df.columns.tolist().index(detected_col) + 1
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
                        if mapped_col:
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
                
                # Validate and import
                missing_cols = [col for col in required_columns.keys() 
                              if col not in column_mapping or not column_mapping[col]]
                if missing_cols:
                    st.error(f"Missing required columns: {', '.join(missing_cols)}")
                else:
                    source_cols = list(column_mapping.values())
                    duplicates = [col for col in source_cols if source_cols.count(col) > 1]
                    if duplicates:
                        st.error(f"Column '{duplicates[0]}' is mapped to multiple target fields.")
                    else:
                        if st.button("Preview Mapped Data"):
                            mapped_df = pd.DataFrame()
                            for target_col, source_col in column_mapping.items():
                                if source_col and source_col in df.columns:
                                    mapped_df[target_col] = df[source_col].copy()
                            
                            st.write("### Preview of Mapped Data")
                            st.dataframe(mapped_df.head())
                            
                            st.session_state.original_df = df.copy()
                            st.session_state.column_mapping = column_mapping
                            st.session_state.mapped_df = mapped_df
                            st.session_state.ready_to_import = True
                        
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
                                    
                                    # Import the data
                                    result = st.session_state.admin.import_chat_room(
                                        project_id,
                                        temp_file,
                                        room_name if container_id is None else None,
                                        container_id=container_id,
                                        metadata_columns=column_mapping
                                    )
                                    
                                    progress_bar.progress(75)
                                    status_text.text("Processing data...")
                                    
                                    # Clean up
                                    if os.path.exists(temp_file):
                                        os.remove(temp_file)
                                    
                                    progress_bar.progress(100)
                                    status_text.text("Import complete!")
                                    
                                    # Success message
                                    container_id = result.get('container_id')
                                    st.success(f"Data imported successfully to container #{container_id}!")
                                    
                                    if 'mapped_columns' in result:
                                        st.write("### Column Mappings Used:")
                                        mapping_df = pd.DataFrame([
                                            {"Field": k, "CSV Column": v} 
                                            for k, v in result['mapped_columns'].items() 
                                            if v is not None
                                        ])
                                        st.table(mapping_df)
                                    
                                    st.write(f"**Items imported:** {result.get('items_imported', 0)}")
                                    
                                    # Clear import state
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
                                    st.session_state.ready_to_import = False
                                    if hasattr(st.session_state, 'mapped_df'):
                                        del st.session_state.mapped_df
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")
                st.error("Please ensure your CSV file is properly formatted.") 