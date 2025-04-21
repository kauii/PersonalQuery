import os
import json
from typing import List, Dict, Literal
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage

CHAT_DIR = os.path.join(os.path.dirname(__file__), "chats")
os.makedirs(CHAT_DIR, exist_ok=True)


def chat_file_path(chat_id: str) -> str:
    return os.path.join(CHAT_DIR, f"{chat_id}.json")


def save_memory(chat_id: str, memory: ConversationBufferMemory):
    path = os.path.join(CHAT_DIR, f"{chat_id}.json")
    os.makedirs(CHAT_DIR, exist_ok=True)

    data = []
    for msg in memory.chat_memory.messages:
        if isinstance(msg, AIMessage):
            data.append({
                "type": "ai",
                "content": msg.content,
                "meta": msg.additional_kwargs.get("meta")  # ✅ preserve meta
            })
        else:
            data.append({
                "type": "human",
                "content": msg.content
            })

    with open(path, "w") as f:
        json.dump(data, f, indent=2)



def load_memory(chat_id: str) -> ConversationBufferMemory:
    memory = ConversationBufferMemory(return_messages=True)
    path = os.path.join(CHAT_DIR, f"{chat_id}.json")
    if not os.path.exists(path):
        return memory

    with open(path, "r") as f:
        chat_data = json.load(f)

    for entry in chat_data:
        if entry["type"] == "human":
            memory.chat_memory.add_user_message(entry["content"])
        else:
            memory.chat_memory.messages.append(
                AIMessage(
                    content=entry["content"],
                    additional_kwargs={"meta": entry.get("meta", {})}
                )
            )

    return memory



def list_chats() -> List[str]:
    return [f.removesuffix(".json") for f in os.listdir(CHAT_DIR) if f.endswith(".json")]
