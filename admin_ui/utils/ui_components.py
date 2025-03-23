"""
Core UI components for the admin interface.
"""
import streamlit as st
from typing import Callable, Any, List, Dict, Optional
import pandas as pd

def notification(message: str, type: str = "info") -> None:
    """Display a notification message using Streamlit.
    
    Args:
        message: The message to display
        type: The type of message ('info', 'success', 'warning', 'error')
    """
    if type == "info":
        st.info(message)
    elif type == "success":
        st.success(message)
    elif type == "warning":
        st.warning(message)
    elif type == "error":
        st.error(message)

def confirm_dialog(title: str, message: str, on_confirm: Callable[[], Any]) -> None:
    """Display a confirmation dialog.
    
    Args:
        title: The dialog title
        message: The confirmation message
        on_confirm: Callback function to execute if confirmed
    """
    with st.expander(title):
        st.write(message)
        if st.button("Confirm", key=f"confirm_{title.lower().replace(' ', '_')}"):
            on_confirm()

def display_data_table(data: List[Dict], key: str) -> None:
    """Display data in a table format.
    
    Args:
        data: List of dictionaries containing the data
        key: Unique key for the table
    """
    if not data:
        st.info("No data to display.")
        return
        
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Display the table using the correct parameters
    st.dataframe(
        df,
        use_container_width=True
    )

def loading_spinner(message: str = "Processing...") -> None:
    """Display a loading spinner with a message.
    
    Args:
        message: The message to display while loading
    """
    with st.spinner(message):
        st.empty()  # Creates space for the spinner 