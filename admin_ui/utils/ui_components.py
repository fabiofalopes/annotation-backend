import streamlit as st
import pandas as pd
from typing import Callable, List, Dict, Any, Optional

def display_data_table(data: List[Dict[str, Any]], columns: List[str] = None):
    """Display data in a formatted table with pagination"""
    if not data:
        st.info("No data to display.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Select columns if specified
    if columns:
        df = df[columns]
    
    # Display the dataframe
    st.dataframe(df, use_container_width=True)

def confirm_dialog(title: str, message: str, on_confirm: Callable, on_cancel: Optional[Callable] = None):
    """Display a confirmation dialog with confirm/cancel buttons"""
    with st.container():
        st.subheader(title)
        st.warning(message)
        cols = st.columns(2)
        with cols[0]:
            if st.button("Confirm", type="primary", key=f"confirm_{id(on_confirm)}"):
                on_confirm()
        with cols[1]:
            if st.button("Cancel", type="secondary", key=f"cancel_{id(on_confirm)}"):
                if on_cancel:
                    on_cancel()

def notification(message: str, type: str = "info"):
    """Display a notification message"""
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    elif type == "warning":
        st.warning(message)
    else:
        st.info(message)

def form_section(title: str = None):
    """Create a form section with consistent styling"""
    container = st.container()
    if title:
        container.subheader(title)
    return container

def action_button(label: str, icon: str = None, key: str = None, on_click: Callable = None):
    """Create a styled action button"""
    button_label = f"{icon} {label}" if icon else label
    button_key = key or f"btn_{label}_{id(on_click)}"
    
    if st.button(button_label, key=button_key, type="primary"):
        if on_click:
            on_click()
        return True
    return False

def search_filter(data: List[Dict[str, Any]], search_key: str, filter_keys: List[str]):
    """Filter data based on search text"""
    search_text = st.text_input(f"Search {search_key}", key=f"search_{search_key}")
    
    if not search_text:
        return data
    
    search_text = search_text.lower()
    filtered_data = []
    
    for item in data:
        for key in filter_keys:
            if key in item and search_text in str(item[key]).lower():
                filtered_data.append(item)
                break
    
    return filtered_data 