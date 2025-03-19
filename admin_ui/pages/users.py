import streamlit as st
import pandas as pd
from admin_ui.components.data_display import display_data_table, create_expander_section

def render_users_page():
    """Render the users management page"""
    st.title("User Management")
    
    # User List
    with create_expander_section("User List", expanded=True):
        if st.button("Refresh Users", key="refresh_users_button"):
            st.session_state.users = st.session_state.admin.list_users()
        
        if "users" not in st.session_state:
            st.session_state.users = st.session_state.admin.list_users()
        
        if st.session_state.users:
            users_data = [
                {
                    "ID": user["id"],
                    "Username": user["username"],
                    "Email": user["email"],
                    "Role": user["role"],
                    "Active": "Yes" if user["is_active"] else "No"
                }
                for user in st.session_state.users
            ]
            display_data_table(users_data, 
                             columns=["ID", "Username", "Email", "Role", "Active"])
    
    # Create User
    with create_expander_section("Create User"):
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Username", key="new_username")
            new_email = st.text_input("Email", key="new_email")
        with col2:
            new_password = st.text_input("Password", type="password", 
                                       help="Password must be at least 8 characters long",
                                       key="new_password")
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
    with create_expander_section("User Details"):
        user_id = st.number_input("User ID", min_value=1, step=1, key="get_user_id")
        if st.button("Get User", key="get_user_button"):
            try:
                user = st.session_state.admin.get_user(user_id)
                st.json(user)
            except Exception as e:
                st.error(f"Error getting user: {e}")
    
    # Delete User
    with create_expander_section("Delete User"):
        delete_user_id = st.number_input("User ID to Delete", min_value=1, step=1, 
                                       key="delete_user_id")
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