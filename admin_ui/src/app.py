import streamlit as st
from streamlit_option_menu import option_menu

from pages.users import users_page
from pages.projects import render_projects_page
from pages.settings import render_settings_page
from utils.auth import check_auth, logout

# Configure page
st.set_page_config(
    page_title="Admin Dashboard",
    #page_icon="��",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# Hide default menu and footer
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def main():
    """Main function to render the admin dashboard"""
    # Check authentication
    if not check_auth():
        return

    # Sidebar navigation
    with st.sidebar:
        selected = option_menu(
            menu_title="Navigation",
            options=["Projects", "Users", "Settings"],
            icons=["folder", "people", "gear"],
            menu_icon="cast",
            default_index=0,
        )
        
        # Logout button
        if st.button("Logout"):
            logout()
            st.rerun()

    # Render selected page
    if selected == "Projects":
        render_projects_page()
    elif selected == "Users":
        users_page()
    elif selected == "Settings":
        render_settings_page()

if __name__ == "__main__":
    main() 