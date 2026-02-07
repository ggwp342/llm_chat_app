import streamlit as st
import requests
import uuid

# --- CONFIGURATION ---
BASE_URL = "http://localhost:8000"
CHAT_URL = f"{BASE_URL}/chat"
HISTORY_URL = f"{BASE_URL}/history"
SESSIONS_URL = f"{BASE_URL}/sessions"

# UI Constants
USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; }
    .stRadio > div { overflow-y: auto; max-height: 60vh; padding-right: 10px; }
    .stChatMessage { padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Intelligent Chat Assistant")

# --- STATE INITIALIZATION ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "prompt_trigger" not in st.session_state:
    st.session_state.prompt_trigger = None

# --- SIDEBAR ---
with st.sidebar:
    st.header("🗂️ Chat Sessions")
    
    # New Chat
    if st.button("➕ New Conversation", use_container_width=True, type="primary"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = [] 
        st.session_state.prompt_trigger = None
        st.rerun()

    st.divider()

    # Fetch Sessions
    session_options = []
    session_titles = {}
    try:
        res = requests.get(SESSIONS_URL)
        if res.status_code == 200:
            data = res.json()
            session_titles = {item["id"]: item["title"] for item in data}
            session_options = [item["id"] for item in data]
    except:
        st.warning("Backend Disconnected")

    if st.session_state.session_id not in session_options:
        session_options.insert(0, st.session_state.session_id)
        session_titles[st.session_state.session_id] = "New Chat..."

    # Session List
    selected_session_id = st.radio(
        "Recent History",
        options=session_options,
        format_func=lambda x: session_titles.get(x, x),
        index=session_options.index(st.session_state.session_id) if st.session_state.session_id in session_options else 0,
        label_visibility="collapsed"
    )

    if selected_session_id != st.session_state.session_id:
        st.session_state.session_id = selected_session_id
        st.session_state.messages = []
        st.rerun()

    # --- EDIT & DELETE OPTIONS ---
    st.divider()
    
    # Only show options if the session exists in backend (not a brand new empty one)
    if st.session_state.session_id in session_titles and session_titles[st.session_state.session_id] != "New Chat...":
        with st.expander("⚙️ Session Options"):
            
            # Edit Title
            new_title = st.text_input("Edit Title", value=session_titles[st.session_state.session_id])
            if st.button("Update Title", use_container_width=True):
                try:
                    requests.patch(f"{SESSIONS_URL}/{st.session_state.session_id}/title", json={"title": new_title})
                    st.success("Title updated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update: {e}")

            # Delete Session
            st.markdown("---")
            if st.button("🗑️ Delete Chat", type="primary", use_container_width=True):
                try:
                    requests.delete(f"{SESSIONS_URL}/{st.session_state.session_id}")
                    # Reset to new chat
                    st.session_state.session_id = str(uuid.uuid4())
                    st.session_state.messages = []
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete: {e}")

# --- LOGIC & MAIN INTERFACE ---
# (Keep the rest of your app.py logic exactly the same as before)
# ...

if not st.session_state.messages:
    try:
        res = requests.get(f"{HISTORY_URL}/{st.session_state.session_id}")
        if res.status_code == 200:
            history_data = res.json()
            for msg in history_data:
                content = msg['parts'][0] if msg['parts'] else ""
                st.session_state.messages.append({"role": msg["role"], "content": content})
    except Exception:
        pass

# Welcome Screen
if not st.session_state.messages:
    st.markdown("### 👋 Hello! How can I help you today?")

# Chat Display
for message in st.session_state.messages:
    role = message["role"]
    avatar = USER_AVATAR if role == "user" else BOT_AVATAR
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

# Input Handling
user_input = st.chat_input("Type your message here...")

if st.session_state.prompt_trigger:
    user_input = st.session_state.prompt_trigger
    st.session_state.prompt_trigger = None

if user_input:
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        response_placeholder = st.empty()
        full_response = ""
        with st.spinner("Thinking..."):
            try:
                payload = {"session_id": st.session_state.session_id, "message": user_input}
                with requests.post(CHAT_URL, json=payload, stream=True) as response:
                    if response.status_code == 200:
                        for chunk in response.iter_content(chunk_size=None):
                            if chunk:
                                text_chunk = chunk.decode("utf-8")
                                full_response += text_chunk
                                response_placeholder.markdown(full_response + "▌")
                        response_placeholder.markdown(full_response)
                        st.session_state.messages.append({"role": "model", "content": full_response})
                    else:
                        st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
