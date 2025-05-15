from fastapi import FastAPI, Request, Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from chat_engine import run_chat, get_chat_history, initialize, delete_chat, rename_chat
from helper.chat_utils import get_next_thread_id, list_chats

initialize()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with ["http://localhost:5173"] for dev if needed
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


@app.post("/chats")
def create_chat():
    """Create a new chat and return its thread ID."""
    chat_id = get_next_thread_id()
    return {"chat_id": chat_id}


@app.post("/chat")
async def chat(request: Request):
    """Send a message to a chat and get a response."""
    data = await request.json()
    question = data.get("question", "")
    chat_id = data.get("chat_id", "1")
    response = run_chat(question, chat_id)
    return JSONResponse(content=response)


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