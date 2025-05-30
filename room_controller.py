# controller/room_controller.py
import streamlit as st
import sqlite3

# DB helper functions
def get_chatrooms():
    conn = sqlite3.connect("chat.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS chatrooms (room TEXT PRIMARY KEY, creator TEXT)")
    cur.execute("SELECT room FROM chatrooms")
    rooms = [row[0] for row in cur.fetchall()]
    conn.close()
    return rooms

def create_chatroom(room, creator):
    conn = sqlite3.connect("chat.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS chatrooms (room TEXT PRIMARY KEY, creator TEXT)")
    cur.execute("INSERT OR IGNORE INTO chatrooms (room, creator) VALUES (?, ?)", (room, creator))
    conn.commit()
    conn.close()

def manage_chatrooms():
    st.sidebar.header("📁 Chatroom Management")
    chatrooms = get_chatrooms()
    selected_room = st.sidebar.selectbox("Join a chatroom", chatrooms)
    new_room = st.sidebar.text_input("Or create new chatroom")

    if st.sidebar.button("Create Chatroom") and new_room:
        create_chatroom(new_room, st.session_state["username"])
        st.session_state["chatroom"] = new_room
        st.rerun()

    if st.sidebar.button("Enter Room") and selected_room:
        st.session_state["chatroom"] = selected_room
        st.rerun()
