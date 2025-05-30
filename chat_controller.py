# controller/chat_controller.py
import streamlit as st
import sqlite3
import base64
import mimetypes
from datetime import datetime, timedelta

# DB helpers
def get_room_creator(room):
    conn = sqlite3.connect("chat.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS chatrooms (room TEXT PRIMARY KEY, creator TEXT)")
    cur.execute("SELECT creator FROM chatrooms WHERE room=?", (room,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def get_messages(room):
    conn = sqlite3.connect("chat.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS messages (room TEXT, user TEXT, text TEXT, timestamp TEXT)")
    cur.execute("SELECT rowid, user, text, timestamp FROM messages WHERE room=? ORDER BY rowid ASC", (room,))
    rows = cur.fetchall()
    conn.close()
    return rows

def save_message(room, user, text):
    conn = sqlite3.connect("chat.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS messages (room TEXT, user TEXT, text TEXT, timestamp TEXT)")
    cur.execute("INSERT INTO messages (room, user, text, timestamp) VALUES (?, ?, ?, ?)",
                (room, user, text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_user_color(username):
    import hashlib
    colors = ["#FFECB3", "#C8E6C9", "#BBDEFB", "#F8BBD0", "#D1C4E9", "#B2EBF2"]
    return colors[int(hashlib.sha256(username.encode()).hexdigest(), 16) % len(colors)]

def human_readable_time(ts_str):
    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    delta = datetime.now() - ts
    if delta < timedelta(minutes=1):
        return "just now"
    elif delta < timedelta(hours=1):
        return f"{int(delta.seconds/60)} minutes ago"
    elif delta < timedelta(days=1):
        return f"{int(delta.seconds/3600)} hours ago"
    else:
        return ts.strftime("%b %d, %H:%M")

def render_chat_interface():
    messages = get_messages(st.session_state["chatroom"])
    creator = get_room_creator(st.session_state["chatroom"])

    st.sidebar.subheader("👥 Users in Room")
    user_set = sorted(set([msg[1] for msg in messages]))
    for u in user_set:
        st.sidebar.markdown(f"- {'🟢 ' if u == st.session_state['username'] else ''}{u}")

    chat_container = st.container()
    with chat_container:
        for _, user, text, timestamp in messages:
            is_self = user == st.session_state["username"]
            align_style = "float: right; clear: both;" if is_self else "float: left; clear: both;"
            bg_color = "#DCF8C6" if is_self else get_user_color(user)
            creator_badge = " 🛡️" if user == creator else ""
            timestamp_str = human_readable_time(timestamp)
            st.markdown(f"""
                <div style='{align_style} margin: 8px 0; width: fit-content;'>
                    <div style='background-color: {bg_color}; padding: 10px 15px; 
                                border-radius: 10px; max-width: 600px;
                                font-family: Arial; font-size: 14px;'>
                        <b>{'You' if is_self else user}{creator_badge}</b><br/>
                        {text}<br/>
                        <small style='font-size: 10px; color: gray;'>{timestamp_str}</small>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.divider()
    user_input = st.text_area("Type your message:", key="input", height=80)
    upload = st.file_uploader("Upload file (image/document)", type=["png", "jpg", "jpeg", "pdf", "docx", "txt"], accept_multiple_files=True)

    if user_input:
        st.session_state["typing"] = True
    else:
        st.session_state["typing"] = False

    if st.session_state["typing"]:
        st.caption("🟡 You are typing...")

    if st.button("Send") or user_input.endswith("\n"):
        final_message = user_input.strip()
        if final_message:
            save_message(st.session_state["chatroom"], st.session_state["username"], final_message)
            st.session_state["input"] = ""  #Clear the input
        if upload:
            for file in upload:
                uploaded_name = file.name
                encoded = base64.b64encode(file.getvalue()).decode("utf-8")
                mime_type, _ = mimetypes.guess_type(uploaded_name)
                if mime_type and mime_type.startswith("image"):
                    file_html = f"<img src='data:{mime_type};base64,{encoded}' width='200'/><br/><small>{uploaded_name}</small>"
                elif mime_type in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                    file_url = f"data:{mime_type};base64,{encoded}"
                    file_html = f"<a href='{file_url}' download='{uploaded_name}' target='_blank'>📄 {uploaded_name}</a>"
                else:
                    file_html = f"📎 {uploaded_name} uploaded."
                save_message(st.session_state["chatroom"], st.session_state["username"], file_html)
        st.session_state["typing"] = False
        st.rerun()
