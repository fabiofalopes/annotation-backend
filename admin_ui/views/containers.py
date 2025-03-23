"""
Containers view module for the Admin UI.
"""
import streamlit as st
from typing import Dict, List

from admin_ui.utils.ui_components import (
    notification,
    confirm_dialog,
    display_data_table,
    loading_spinner
)

def format_container_data(containers: List[Dict]) -> List[Dict]:
    """Format container data for display.
    
    Args:
        containers: List of container dictionaries from the API
        
    Returns:
        List of formatted container dictionaries
    """
    formatted_containers = []
    for container in containers:
        formatted_containers.append({
            "ID": container.get("id", "N/A"),
            "Name": container.get("name", "N/A"),
            "Project": container.get("project_name", "N/A"),
            "Status": container.get("status", "N/A"),
            "Created At": container.get("created_at", "N/A")
        })
    return formatted_containers

def show_containers_view() -> None:
    """Render the containers view."""
    st.title("📦 Container Management")
    
    try:
        # Fetch and display containers
        containers = st.session_state.admin.list_containers()
        if containers:
            formatted_containers = format_container_data(containers)
            
            # Display containers table
            st.subheader("Current Containers")
            display_data_table(
                data=formatted_containers,
                key="containers_table"
            )
            
            # Container actions
            st.subheader("Container Actions")
            for container in containers:
                cols = st.columns([3, 1])
                with cols[0]:
                    st.write(f"**{container['name']}** ({container['status']})")
                with cols[1]:
                    confirm_dialog(
                        title=f"Delete {container['name']}",
                        message=f"Are you sure you want to delete container {container['name']}?",
                        on_confirm=lambda cid=container['id']: delete_container(cid)
                    )
        else:
            st.info("No containers found.")
            
    except Exception as e:
        notification(f"Failed to load containers: {str(e)}", "error")

def delete_container(container_id: str) -> None:
    """Delete a container.
    
    Args:
        container_id: The ID of the container to delete
    """
    try:
        st.session_state.admin.delete_container(container_id)
        notification("Container deleted successfully!", "success")
        st.rerun()  # Refresh to remove the deleted container
    except Exception as e:
        notification(f"Failed to delete container: {str(e)}", "error") 