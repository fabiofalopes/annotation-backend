import streamlit as st
import pandas as pd
import traceback
import json
import requests
import uuid
from admin_ui.utils.ui_components import display_data_table, confirm_dialog, notification
from admin_ui.api_client import AnnoBackendAdmin

# Initialize session state and admin instance safely
# if "admin" not in st.session_state:  <-- REMOVE THIS
#     st.session_state["admin"] = None
# admin = st.session_state.get("admin") <-- REMOVE THIS

def show_containers_view():
    admin = st.session_state.get("admin")
    # Check if the user is logged in (admin object exists)
    if admin is None:
        st.error("Please log in to access the Containers page.")
        st.stop()  # Stop execution here

    # Page title
    st.title("Data Container Management")  # Clearer title

    # Debug info in sidebar (keep for now)
    with st.sidebar:
        st.write("Debug Info:")
        st.write(f"API URL: {admin.base_url if admin else 'Not set'}")
        st.write(f"Token present: {'Yes' if admin and admin.token else 'No'}")

    # Containers List with Quick Actions
    st.subheader("Data Containers") # Clearer subheader
    if st.button("🔄 Refresh"):
        if "containers" in st.session_state:
            del st.session_state["containers"]
        st.rerun()

    # Get containers data
    containers = st.session_state.get("containers") or admin.list_containers()
    st.session_state["containers"] = containers

    if containers:
        # Display each container as a card with actions
        for container in containers:
            with st.container():
                col1, col2 = st.columns([5, 1])  # Adjusted column widths
                with col1:
                    st.markdown(f"### {container['name']}")
                    st.markdown(f"**Type:** {container.get('type', 'Unknown')} | **Project ID:** {container.get('project_id', 'Unknown')}")  # Removed Docker-related info
                    st.caption(f"ID: {container['id']}") # Show ID

                with col2:
                    # Delete Container
                    if st.button("🗑️ Delete", key=f"delete_container_{container['id']}", type="secondary"):
                        st.session_state.confirm_delete_container = container['id']
                        st.rerun()

                # Show confirmation dialog if delete button was clicked
                if st.session_state.get("confirm_delete_container") == container['id']:
                    with st.container():
                        st.warning(f"Are you sure you want to delete data container **{container['name']}**?") # Clearer warning

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Yes, Delete", key=f"confirm_container_{container['id']}", type="primary"):
                                try:
                                    admin.delete_container(container['id'])
                                    st.success(f"Data container {container['name']} deleted successfully!") # Clearer success message
                                    if "containers" in st.session_state:
                                        del st.session_state["containers"]
                                    if "confirm_delete_container" in st.session_state:
                                        del st.session_state["confirm_delete_container"]
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")

                        with col2:
                            if st.button("Cancel", key=f"cancel_container_{container['id']}", type="secondary"):
                                if "confirm_delete_container" in st.session_state:
                                    del st.session_state["confirm_delete_container"]
                                st.rerun()

                st.divider()
    else:
        st.info("No data containers found.") # Clearer message 