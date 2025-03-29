import streamlit as st

def render_settings_page():
    """Render the settings page"""
    st.title("⚙️ Settings")
    
    # API Configuration Section
    st.header("API Configuration")
    with st.form("api_settings"):
        api_url = st.text_input("API Base URL", value=st.session_state.get("api_url", "http://localhost:8000"))
        save = st.form_submit_button("Save Settings")
        
        if save:
            st.session_state.api_url = api_url
            st.success("Settings saved successfully!")
    
    # Theme Settings
    st.header("Theme Settings")
    theme = st.selectbox(
        "Color Theme",
        ["Light", "Dark"],
        index=0 if st.session_state.get("theme", "Light") == "Light" else 1
    )
    if theme != st.session_state.get("theme"):
        st.session_state.theme = theme
        st.success("Theme updated! Please refresh the page to see changes.") 