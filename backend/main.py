from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from backend.models import ChatRequest, TitleUpdateRequest # Import new model
from backend.llm_service import stream_chat_response
from backend.database import (
    get_chat_history, 
    get_all_sessions, 
    delete_session_db, 
    update_session_title_db
)

app = FastAPI()

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    return StreamingResponse(
        stream_chat_response(request.session_id, request.message),
        media_type="text/plain"
    )

@app.get("/history/{session_id}")
async def history_endpoint(session_id: str):
    return get_chat_history(session_id)

@app.get("/sessions")
async def sessions_endpoint():
    return get_all_sessions()

# --- NEW ENDPOINTS ---

@app.delete("/sessions/{session_id}")
async def delete_session_endpoint(session_id: str):
    success = delete_session_db(session_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete session")
    return {"status": "success"}

@app.patch("/sessions/{session_id}/title")
async def update_title_endpoint(session_id: str, request: TitleUpdateRequest):
    success = update_session_title_db(session_id, request.title)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update title")
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
