# app.py

import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Import controller modules
from controller.login_controller import login_interface
from controller.room_controller import manage_chatrooms
from controller.chat_controller import render_chat_interface

# Auto-refresh every 5 seconds
st_autorefresh(interval=5000, limit=None, key="chat_refresh")

# 🌙 Dark mode toggle
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

# Apply dark mode styles
if st.session_state["dark_mode"]:
    st.markdown("""
        <style>
        body, .stApp {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        </style>
    """, unsafe_allow_html=True)

# Initialize session state keys
for key in ["username", "chatroom", "typing", "reactions"]:
    if key not in st.session_state:
        st.session_state[key] = {} if key == "reactions" else None if key != "typing" else False

# Step 1: Login
login_interface()

# Step 2: Manage chatrooms
manage_chatrooms()

if "username" in st.session_state:
    st.sidebar.checkbox("🌙 Dark Mode", key="dark_mode")

# Step 3: Render chat interface
if st.session_state["chatroom"]:
    render_chat_interface()
else:
    st.info("Please select or create a chatroom to begin.")