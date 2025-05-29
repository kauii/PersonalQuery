from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
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


@app.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            question = data.get("question", "")
            chat_id = data.get("chat_id", "1")

            async def send_update(update: dict):
                await websocket.send_json(update)

            def on_update(update: dict):
                import asyncio
                asyncio.create_task(send_update(update))

            msg = run_chat(question, chat_id)

            await websocket.send_json(msg)

    except WebSocketDisconnect:
        print("Client disconnected")



@app.post("/chats")
def create_chat():
    chat_id = get_next_thread_id()
    return {"chat_id": chat_id}


@app.get("/chats")
def get_all_chats():
    return {"chats": list_chats()}


@app.get("/chats/{chat_id}")
def get_chat(chat_id: str):
    return get_chat_history(chat_id)


@app.delete("/chats/{chat_id}")
def remove_chat(chat_id: str):
    return delete_chat(chat_id)


@app.put("/chats/{chat_id}/rename")
def rename_chat_endpoint(chat_id: str, new_title: str = Body(..., embed=True)):
    return rename_chat(chat_id, new_title)