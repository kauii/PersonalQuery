# py-backend/server_rest.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from chat_engine import run_chat

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
    response = run_chat(question)
    return JSONResponse(content={
        "answer": response["answer"],
        "query": response["query"],
        "activities": response["activities"],
        "tables": response["tables"],
        "result": response["result"]
    })
