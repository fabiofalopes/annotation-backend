import streamlit as st
import pandas as pd
import json
from admin_ui.components.data_display import (
    display_data_table,
    create_expander_section,
    display_chat_messages
)

def render_containers_page():
    """Render the data containers management page"""
    st.title("Data Container Management")
    
    # Container List with Type Filter
    with create_expander_section("Container List", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            filter_project_id = st.number_input(
                "Filter by Project ID (0 for all)",
                min_value=0,
                step=1,
                key="filter_project_id"
            )
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
            containers_data = [
                {
                    "ID": container["id"],
                    "Name": container["name"],
                    "Type": container["type"],
                    "Project ID": container["project_id"],
                    "Items Count": container.get("items_count", "N/A")
                }
                for container in st.session_state.containers
            ]
            display_data_table(containers_data,
                             columns=["ID", "Name", "Type", "Project ID", "Items Count"])
            
            # Quick view buttons for each container
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
                    
                    # Prepare messages data
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
                            messages = sorted(messages, 
                                           key=lambda x: int(x["Turn ID"]) if x["Turn ID"].isdigit() else float('inf'))
                        except:
                            pass
                        display_data_table(messages,
                                         columns=["ID", "Turn ID", "User", "Message", "Reply To", "Thread"])
                    else:
                        # Use the shared chat message display component
                        display_chat_messages(messages, thread_view=(view_type == "Thread View"))
                else:
                    # Generic data item display
                    items_data = [
                        {
                            "ID": item["id"],
                            "Content": item["content"],
                            "Metadata": json.dumps(item.get("item_metadata", {}))
                        }
                        for item in container["items"]
                    ]
                    display_data_table(items_data,
                                     columns=["ID", "Content", "Metadata"])
        except Exception as e:
            st.error(f"Error loading container: {str(e)}")
            st.session_state.view_container_id = None 