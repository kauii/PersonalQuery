from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chat_engine import run_chat, get_chat_history, initialize, delete_chat, rename_chat, resume_stream
from helper.chat_utils import get_next_thread_id, list_chats
from helper.ws_utils import resolve_approval

initialize()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with ["http://localhost:5173"] for dev if needed
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            print(data)

            question = data.get("question", "")
            chat_id = data.get("chat_id", "1")
            top_k = data.get("top_k", 150)
            auto_approve = data.get("auto_approve", False)
            print(top_k)
            print(auto_approve)

            async def on_update(update: dict):
                await websocket.send_json(update)

            msg = await run_chat(question, chat_id, top_k, auto_approve, on_update=on_update)
            if msg:
                await websocket.send_json(msg)

    except WebSocketDisconnect:
        print("Client disconnected")


@app.post("/chats")
def create_chat():
    """Create a new chat and return its thread ID."""
    chat_id = get_next_thread_id()
    return {"chat_id": chat_id}


@app.get("/chats")
def get_all_chats():
    """Return a list of all chat thread IDs."""
    return {"chats": list_chats()}


@app.get("/chats/{chat_id}")
def get_chat(chat_id: str):
    """Return message history for a given chat."""
    return get_chat_history(chat_id)


@app.delete("/chats/{chat_id}")
def remove_chat(chat_id: str):
    return delete_chat(chat_id)


@app.put("/chats/{chat_id}/rename")
def rename_chat_endpoint(chat_id: str, new_title: str = Body(..., embed=True)):
    """Rename an existing chat by its chat_id."""
    return rename_chat(chat_id, new_title)


@app.post("/approval")
async def handle_approval(request: Request):
    payload = await request.json()
    chat_id = payload.get("chat_id")
    approval = payload.get("approval")

    print(f"✅ Approval received: chat_id={chat_id}, approval={approval}")

    if not isinstance(approval, bool):
        return {"status": "error", "message": "Missing or invalid 'approval' boolean."}

    if approval:
        msg = resume_stream(chat_id)
        return msg
    else:
        return {}