# controller/login_controller.py
import streamlit as st

def login_interface():
    if not st.session_state["username"]:
        st.title("🔐 Login")
        username = st.text_input("Enter username")
        if st.button("Login") and username:
            st.session_state["username"] = username
            st.rerun()
        st.stop()
