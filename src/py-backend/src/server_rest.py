from fastapi import FastAPI, Request
from langchain.memory import ConversationBufferMemory
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from chat_engine import run_chat
from chat_store import list_chats, load_memory, save_memory

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with ["http://localhost:5173"] for dev if needed
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    question = data.get("question", "")
    chat_id = data.get("chat_id", "default")

    response = run_chat(question, chat_id)
    return JSONResponse(content=response)


@app.get("/chats")
def get_all_chats():
    return {"chats": list_chats()}


@app.get("/chats/{chat_id}")
def get_chat(chat_id: str):
    memory = load_memory(chat_id)
    return {
        "messages": [msg.dict() for msg in memory.chat_memory.messages]
    }


@app.post("/chats")
def create_chat():
    import uuid
    chat_id = str(uuid.uuid4())
    save_memory(chat_id, ConversationBufferMemory(return_messages=True))
    return {"chat_id": chat_id}
