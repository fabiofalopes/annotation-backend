import streamlit as st
import pandas as pd
from admin_ui.utils.ui_components import display_data_table, confirm_dialog, notification

# Get admin instance
admin = st.session_state.admin

# Page title
st.title("User Management")

# Create User Section
with st.container():
    st.subheader("Create New User")
    
    # Use a Streamlit form to handle the user creation
    # Generate a unique key for the form using a counter in session state
    if "user_form_counter" not in st.session_state:
        st.session_state.user_form_counter = 0
    st.session_state.user_form_counter += 1
    form_key = f"create_user_form_{st.session_state.user_form_counter}"

    with st.form(key=form_key):
        cols = st.columns([2, 2, 2, 1])
        with cols[0]:
            new_username = st.text_input(
                "Username",
                key=f"form_username_{st.session_state.user_form_counter}",
                placeholder="Enter username"
            )
        with cols[1]:
            new_email = st.text_input(
                "Email",
                key=f"form_email_{st.session_state.user_form_counter}",
                placeholder="user@example.com"
            )
        with cols[2]:
            new_password = st.text_input(
                "Password",
                type="password",
                key=f"form_password_{st.session_state.user_form_counter}",
                help="Leave blank to auto-generate"
            )
        with cols[3]:
            new_role = st.selectbox(
                "Role",
                ["admin", "annotator"],
                index=1,
                key=f"form_role_{st.session_state.user_form_counter}"
            )

        # Form submit button - use st.form_submit_button instead of st.button
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
                    # Refresh users list
                    st.session_state.users = admin.list_users()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating user: {e}")

st.divider()

# Users List with Quick Actions
st.subheader("Users")
refresh_col, spacer = st.columns([1, 5])
with refresh_col:
    if st.button("🔄 Refresh", key=f"users_refresh_{st.session_state.user_form_counter}"):
        st.session_state.users = admin.list_users()

# Get users data
if "users" not in st.session_state:
    st.session_state.users = admin.list_users()

if st.session_state.users:
    # Display each user as a card with actions
    for idx, user in enumerate(st.session_state.users):
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"### {user['username']}")
                st.markdown(f"**Role:** {user['role']} | **ID:** {user['id']}")
                st.markdown(f"📧 {user['email']}")
                status = "🟢 Active" if user['is_active'] else "🔴 Inactive"
                st.markdown(f"_{status}_")
            
            with col2:
                # Toggle Active Status
                button_text = "Deactivate" if user['is_active'] else "Activate"
                button_emoji = "🔒" if user['is_active'] else "🔓"
                if st.button(
                    f"{button_emoji} {button_text}", 
                    key=f"users_toggle_{idx}_{user['id']}_{st.session_state.user_form_counter}", 
                    type="secondary"
                ):
                    try:
                        if user['is_active']:
                            admin.deactivate_user(user['id'])
                        else:
                            admin.activate_user(user['id'])
                        st.session_state.users = admin.list_users()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error toggling user status: {e}")
            
            with col3:
                # Delete User
                if st.button(
                    "🗑️ Delete", 
                    key=f"users_delete_{idx}_{user['id']}_{st.session_state.user_form_counter}", 
                    type="secondary"
                ):
                    confirm_key = f"users_confirm_delete_{idx}_{user['id']}"
                    st.session_state[confirm_key] = True
            
            # Show confirmation dialog if delete button was clicked
            confirm_key = f"users_confirm_delete_{idx}_{user['id']}"
            if confirm_key in st.session_state and st.session_state[confirm_key]:
                with st.container():
                    st.warning(f"Are you sure you want to delete user **{user['username']}**?")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(
                            "Yes, Delete",
                            key=f"users_confirm_{idx}_{user['id']}_{st.session_state.user_form_counter}",
                            type="primary"
                        ):
                            try:
                                admin.delete_user(user['id'])
                                st.success(f"User {user['username']} deleted successfully!")
                                st.session_state.users = admin.list_users()
                                st.session_state[confirm_key] = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    
                    with col2:
                        if st.button(
                            "Cancel",
                            key=f"users_cancel_{idx}_{user['id']}_{st.session_state.user_form_counter}",
                            type="secondary"
                        ):
                            st.session_state[confirm_key] = False
                            st.rerun()
            
            st.divider()
else:
    st.info("No users found. Create one using the form above.") 