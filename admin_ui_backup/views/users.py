import streamlit as st
import pandas as pd
import uuid
from admin_ui.utils.ui_components import display_data_table, confirm_dialog, notification
from admin_ui.api_client import AnnoBackendAdmin

# Initialize admin instance safely
# if "admin" not in st.session_state:
#     st.session_state["admin"] = None
# admin = st.session_state.get("admin")

def show_users_view():
    admin = st.session_state.get("admin")
    # Check if the user is logged in (admin object exists)
    if admin is None:
        st.error("Please log in to access the Users page.")
        st.stop()  # Stop execution here

    # Page title
    st.title("User Management")

    # Create User Section
    with st.container():
        st.subheader("Create New User")

        # Simplified form key
        with st.form(key="create_user_form"):
            cols = st.columns([2, 2, 2, 1])
            with cols[0]:
                new_username = st.text_input("Username", placeholder="Enter username")
            with cols[1]:
                new_email = st.text_input("Email", placeholder="user@example.com")
            with cols[2]:
                new_password = st.text_input("Password", type="password", help="Leave blank to auto-generate")
            with cols[3]:
                new_role = st.selectbox("Role", ["admin", "annotator"], index=1)

            submit_button = st.form_submit_button("Create User")

            if submit_button:
                if not new_username or not new_email:
                    st.error("Username and email are required")
                else:
                    try:
                        user = admin.create_user(
                            new_username, new_email, new_password if new_password else None, new_role
                        )
                        st.success(f"User {user['username']} created successfully!")
                        # Refresh users list - simpler
                        if "users" in st.session_state:
                            del st.session_state["users"]
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating user: {e}")

    st.divider()

    # Users List
    st.subheader("Users")
    if st.button("🔄 Refresh"): # Simplified refresh
        if "users" in st.session_state:
            del st.session_state["users"]
        st.rerun()

    # Get users data - simpler
    users = st.session_state.get("users") or admin.list_users()
    st.session_state["users"] = users

    if users:
        for user in users:
            with st.container():
                col1, col2, col3 = st.columns([3,1,1])
                with col1:
                    st.markdown(f"### {user['username']}")
                    st.markdown(f"**Email:** {user['email']} | **Role:** {user['role']} | **ID:** {user['id']}")

                with col2:
                    if st.button("🔑 Reset Password", key=f"reset_{user['id']}"):
                        st.session_state.reset_user = user['id'] # Store just the ID
                        st.rerun()

                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{user['id']}"):
                        st.session_state.delete_user = user['id'] # Store just the ID
                        st.rerun()

                # Handle reset password
                if st.session_state.get("reset_user") == user['id']:
                    with st.container():
                        st.warning(f"Reset password for **{user['username']}**")
                        new_pw = st.text_input("New Password", type="password", key=f"new_pw_{user['id']}")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Confirm", key=f"confirm_reset_{user['id']}") and new_pw:
                                try:
                                    admin.update_user(user['id'], password=new_pw)
                                    st.success("Password reset successfully!")
                                    if "reset_user" in st.session_state:
                                        del st.session_state["reset_user"]
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        with col2:
                            if st.button("Cancel", key=f"cancel_reset_{user['id']}"):
                                if "reset_user" in st.session_state:
                                    del st.session_state["reset_user"]
                                st.rerun()

                # Handle delete confirmation
                if st.session_state.get("delete_user") == user['id']:
                    with st.container():
                        st.warning(f"Delete user **{user['username']}**?")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Confirm", key=f"confirm_delete_{user['id']}"):
                                try:
                                    admin.delete_user(user['id'])
                                    st.success("User deleted successfully!")
                                    if "users" in st.session_state:
                                        del st.session_state["users"]
                                    if "delete_user" in st.session_state:
                                        del st.session_state["delete_user"]
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        with col2:
                            if st.button("Cancel", key=f"cancel_delete_{user['id']}"):
                                if "delete_user" in st.session_state:
                                    del st.session_state["delete_user"]
                                st.rerun()

                st.divider()
    else:
        st.info("No users found.") 