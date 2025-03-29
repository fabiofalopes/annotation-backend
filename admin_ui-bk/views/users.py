"""
Users view module for the Admin UI.
"""
import streamlit as st
from typing import Dict, List

from admin_ui.utils.ui_components import (
    notification,
    confirm_dialog,
    display_data_table,
    loading_spinner
)

def create_user_form() -> None:
    """Render the create user form."""
    with st.form("create_user_form"):
        st.subheader("Create New User")
        
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", options=["annotator", "admin"])
        
        if st.form_submit_button("Create User"):
            try:
                loading_spinner("Creating user...")
                st.session_state.admin.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=role
                )
                notification("User created successfully!", "success")
                st.rerun()  # Refresh to show the new user
            except Exception as e:
                notification(f"Failed to create user: {str(e)}", "error")

def delete_user(user_id: str) -> None:
    """Delete a user.
    
    Args:
        user_id: The ID of the user to delete
    """
    try:
        st.session_state.admin.delete_user(user_id)
        notification("User deleted successfully!", "success")
        st.rerun()  # Refresh to remove the deleted user
    except Exception as e:
        notification(f"Failed to delete user: {str(e)}", "error")

def format_user_data(users: List[Dict]) -> List[Dict]:
    """Format user data for display.
    
    Args:
        users: List of user dictionaries from the API
        
    Returns:
        List of formatted user dictionaries
    """
    formatted_users = []
    for user in users:
        formatted_users.append({
            "ID": user.get("id", "N/A"),
            "Username": user.get("username", "N/A"),
            "Email": user.get("email", "N/A"),
            "Role": user.get("role", "N/A"),
            "Active": "Yes" if user.get("is_active", False) else "No",
            "Created At": user.get("created_at", "N/A")
        })
    return formatted_users

def show_users_view() -> None:
    """Render the users view."""
    st.title("👥 User Management")
    
    # Create user form in the sidebar
    with st.sidebar:
        st.markdown("---")
        create_user_form()
    
    try:
        # Fetch and display users
        users = st.session_state.admin.list_users()
        if users:
            formatted_users = format_user_data(users)
            
            # Display users table
            st.subheader("Current Users")
            display_data_table(
                data=formatted_users,
                key="users_table"
            )
            
            # User actions
            st.subheader("User Actions")
            for user in users:
                cols = st.columns([3, 1])
                with cols[0]:
                    st.write(f"**{user['username']}** ({user['email']})")
                with cols[1]:
                    confirm_dialog(
                        title=f"Delete {user['username']}",
                        message=f"Are you sure you want to delete user {user['username']}?",
                        on_confirm=lambda user_id=user['id']: delete_user(user_id)
                    )
        else:
            st.info("No users found.")
            
    except Exception as e:
        notification(f"Failed to load users: {str(e)}", "error") 