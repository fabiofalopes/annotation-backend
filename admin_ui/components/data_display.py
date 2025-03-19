import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional

def display_data_table(data: List[Dict[Any, Any]], 
                      columns: List[str],
                      key: Optional[str] = None):
    """Display data in a Streamlit table with consistent formatting"""
    if data:
        df = pd.DataFrame(data)
        if columns:
            df = df[columns]
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No data available")

def display_chat_messages(messages: List[Dict[Any, Any]], 
                        thread_view: bool = False):
    """Display chat messages with optional threading"""
    if not messages:
        st.info("No messages available")
        return
    
    if thread_view:
        # Group messages by thread
        threads = {}
        unthreaded = []
        for msg in messages:
            if msg.get("Thread"):
                if msg["Thread"] not in threads:
                    threads[msg["Thread"]] = []
                threads[msg["Thread"]].append(msg)
            else:
                unthreaded.append(msg)
        
        # Display threads
        for thread_id, thread_msgs in threads.items():
            with st.expander(f"Thread {thread_id} ({len(thread_msgs)} messages)", expanded=True):
                for msg in thread_msgs:
                    with st.chat_message(name=msg["User"]):
                        st.write(f"**{msg['User']}** (Turn {msg['Turn ID']})")
                        st.write(msg["Message"])
                        if msg.get("Reply To"):
                            st.caption(f"↩️ Reply to Turn {msg['Reply To']}")
        
        if unthreaded:
            with st.expander(f"Unthreaded Messages ({len(unthreaded)})", expanded=True):
                for msg in unthreaded:
                    with st.chat_message(name=msg["User"]):
                        st.write(f"**{msg['User']}** (Turn {msg['Turn ID']})")
                        st.write(msg["Message"])
                        if msg.get("Reply To"):
                            st.caption(f"↩️ Reply to Turn {msg['Reply To']}")
    else:
        # Display messages in sequence
        for msg in messages:
            with st.chat_message(name=msg["User"]):
                st.write(f"**{msg['User']}** (Turn {msg['Turn ID']})")
                st.write(msg["Message"])
                if msg.get("Reply To"):
                    st.caption(f"↩️ Reply to Turn {msg['Reply To']}")

def create_expander_section(title: str, expanded: bool = False):
    """Create a consistent expander section"""
    return st.expander(title, expanded=expanded) 