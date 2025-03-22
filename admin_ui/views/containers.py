import streamlit as st
import pandas as pd
import json
from admin_ui.utils.ui_components import display_data_table, confirm_dialog, notification

# Get admin instance
admin = st.session_state.admin

# Page title
st.title("Data Dashboard")

# Initialize dashboard counter for unique keys
if "dashboard_counter" not in st.session_state:
    st.session_state.dashboard_counter = 0
st.session_state.dashboard_counter += 1

# Container Filters 
with st.container():
    st.subheader("Data Filters")
    col1, col2 = st.columns(2)
    with col1:
        filter_project_id = st.number_input("Filter by Project ID (0 for all)", min_value=0, step=1, key=f"dashboard_filter_project_id_{st.session_state.dashboard_counter}")
    with col2:
        filter_type = st.selectbox(
            "Filter by Type",
            ["All", "chat_rooms", "documents"],
            key=f"dashboard_filter_type_{st.session_state.dashboard_counter}"
        )
    
    if st.button("🔄 Refresh Data", key=f"dashboard_refresh_button_{st.session_state.dashboard_counter}"):
        try:
            containers = admin.list_containers(
                project_id=filter_project_id if filter_project_id > 0 else None
            )
            if filter_type != "All":
                containers = [c for c in containers if c["type"] == filter_type]
            st.session_state.containers = containers
        except Exception as e:
            st.error(f"Error listing data: {e}")
            st.session_state.containers = []

# Get containers data
if "containers" not in st.session_state:
    try:
        containers = admin.list_containers(
            project_id=filter_project_id if filter_project_id > 0 else None
        )
        if filter_type != "All":
            containers = [c for c in containers if c["type"] == filter_type]
        st.session_state.containers = containers
    except Exception as e:
        st.error(f"Error listing data: {e}")
        st.session_state.containers = []

st.divider()

# Display Data
st.subheader("Data Overview")
if st.session_state.containers:
    # Display each container as a card with actions
    for container in st.session_state.containers:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"### {container['name']}")
                st.markdown(f"**Type:** {container['type']} | **Project ID:** {container['project_id']}")
                items_count = container.get('items_count', 'Unknown')
                st.caption(f"Items: {items_count}")
            
            with col2:
                # View Container Details Button
                if st.button("👁️ View", key=f"dashboard_view_{container['id']}", type="secondary"):
                    st.session_state.view_container_id = container['id']
                    
            with col3:
                # Delete Container
                if st.button("🗑️ Delete", key=f"dashboard_delete_{container['id']}", type="secondary"):
                    confirm_key = f"dashboard_confirm_delete_{container['id']}"
                    st.session_state[confirm_key] = True
            
            # Show confirmation dialog if delete button was clicked
            confirm_key = f"dashboard_confirm_delete_{container['id']}"
            if confirm_key in st.session_state and st.session_state[confirm_key]:
                with st.container():
                    st.warning(f"Are you sure you want to delete **{container['name']}**?")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Yes, Delete", key=f"dashboard_confirm_{container['id']}", type="primary"):
                            try:
                                admin.delete_container(container['id'])
                                st.success(f"Data {container['name']} deleted successfully!")
                                # Refresh containers list
                                containers = admin.list_containers(
                                    project_id=filter_project_id if filter_project_id > 0 else None
                                )
                                if filter_type != "All":
                                    containers = [c for c in containers if c["type"] == filter_type]
                                st.session_state.containers = containers
                                st.session_state[confirm_key] = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    
                    with col2:
                        if st.button("Cancel", key=f"dashboard_cancel_{container['id']}", type="secondary"):
                            st.session_state[confirm_key] = False
                            st.rerun()
            
            st.divider()
            
    # Container Details View
    if hasattr(st.session_state, 'view_container_id') and st.session_state.view_container_id:
        try:
            container = admin.get_container(st.session_state.view_container_id)
            
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
                        st.session_state.pre_selected_container = container['id']
                        # Set navigation to Import page handled by the main navigation
            
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
else:
    st.info("No containers found with the current filters. Try changing the filters or refresh.") 