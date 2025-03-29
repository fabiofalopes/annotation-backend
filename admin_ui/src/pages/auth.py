import streamlit as st
import time
from api.client import login, show_notification

def render_login_page():
    """Render the login page"""
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.title("👋 Welcome Back!")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not username or not password:
                    show_notification("Please enter both username and password", "error")
                else:
                    with st.spinner("Logging in..."):
                        token = login(username, password)
                        if token:
                            st.session_state.token = token
                            st.success("Login successful!")
                            time.sleep(1)  # Give time for success message
                            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True) 