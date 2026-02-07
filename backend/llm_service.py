import os
import google.generativeai as genai
from backend.database import add_message, get_chat_history

# Configure Gemini
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-3-flash-preview')

async def stream_chat_response(session_id: str, user_message: str):
    # 1. Save User Message to DB
    add_message(session_id, "user", user_message)

    # 2. Fetch History from DB to maintain context
    history = get_chat_history(session_id)
    
    # Note: Gemini expects history excluding the current new prompt in start_chat
    # However, since we just added the user message to DB, 'history' contains it.
    # We will separate the history and the current message for the API call 
    # or simply pass the history to the model if using stateless generation.
    
    # Stateless generation approach with history context:
    chat = model.start_chat(history=history[:-1]) # Load everything except last (current)
    
    # 3. Generate Streaming Response
    response_stream = chat.send_message(user_message, stream=True)

    full_response_text = ""

    # 4. Yield chunks and accumulate full text
    for chunk in response_stream:
        if chunk.text:
            full_response_text += chunk.text
            yield chunk.text

    # 5. Save Model Response to DB after stream completes
    add_message(session_id, "model", full_response_text)
