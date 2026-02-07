import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def add_message(session_id: str, role: str, content: str):
    """Saves a message and ensures a session entry exists."""
    
    # 1. Ensure session exists in the 'sessions' table
    # We try to select it first to avoid overwriting custom titles
    try:
        exists = supabase.table("sessions").select("session_id").eq("session_id", session_id).execute()
        
        if not exists.data:
            # If it's a new session, create it with a generated title
            # Truncate content for title
            title = (content[:30] + '..') if len(content) > 30 else content
            supabase.table("sessions").insert({
                "session_id": session_id,
                "title": title
            }).execute()
    except Exception as e:
        print(f"Session creation check failed: {e}")

    # 2. Insert the message
    data = {
        "session_id": session_id,
        "role": role,
        "content": content
    }
    supabase.table("chat_history").insert(data).execute()

def get_all_sessions():
    """Fetches sessions from the dedicated sessions table."""
    try:
        # Fetch from 'sessions' table, ordered by newest first
        response = supabase.table("sessions")\
            .select("session_id, title")\
            .order("created_at", desc=True)\
            .execute()
        
        # Map to the format frontend expects: [{'id': '...', 'title': '...'}]
        return [{"id": item['session_id'], "title": item['title']} for item in response.data]
    except Exception as e:
        print(f"Error fetching sessions: {e}")
        return []

def get_chat_history(session_id: str):
    """Fetches chat history."""
    response = supabase.table("chat_history")\
        .select("role, content")\
        .eq("session_id", session_id)\
        .order("created_at")\
        .execute()
    
    formatted_history = []
    for msg in response.data:
        formatted_history.append({
            "role": msg["role"],
            "parts": [msg["content"]]
        })
    return formatted_history

# --- NEW FUNCTIONS ---

def delete_session_db(session_id: str):
    """Deletes a session and its messages."""
    # If ON DELETE CASCADE is set in SQL, deleting from 'sessions' is enough.
    # If not, we manually delete chat_history first.
    try:
        supabase.table("chat_history").delete().eq("session_id", session_id).execute()
        supabase.table("sessions").delete().eq("session_id", session_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting session: {e}")
        return False

def update_session_title_db(session_id: str, new_title: str):
    """Updates the title of a session."""
    try:
        supabase.table("sessions")\
            .update({"title": new_title})\
            .eq("session_id", session_id)\
            .execute()
        return True
    except Exception as e:
        print(f"Error updating title: {e}")
        return False
