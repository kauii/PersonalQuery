import os
import json
import sqlite3
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.graph import CompiledGraph

from chains.activity_chain import extract_activities
from chains.answer_chain import generate_answer, general_answer
from chains.query_chain import write_query, execute_query
from chains.table_chain import get_tables
from chains.init_chain import classify_question
from schemas import State
from llm_registry import LLMRegistry

THREAD_COUNTER_FILE = os.path.join(os.path.dirname(__file__), "thread_counter.json")
APPDATA_PATH = Path(os.getenv("APPDATA", Path.home()))
CHECKPOINT_DB_PATH = APPDATA_PATH / "personal-analytics" / "chat_checkpoints.db"

graph: CompiledGraph


def initialize():
    global graph

    load_dotenv()

    llm_openai = ChatOpenAI(
        model="gpt-4o",
        temperature=0.0,
        base_url="https://api.openai.com/v1",
        api_key=os.getenv("MY_OPENAI_API_KEY")
    )

    llm_llama31 = ChatOpenAI(
        model="llama31instruct",
        temperature=0.0,
        base_url="http://llm.hasel.dev:20769/v1",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    LLMRegistry.register("openai", llm_openai)
    LLMRegistry.register("llama31", llm_llama31)

    graph_builder = StateGraph(State)

    graph_builder.add_node("classify_question", classify_question)
    graph_builder.add_edge(START, "classify_question")

    graph_builder.add_sequence([
        get_tables,
        extract_activities,
        write_query,
        execute_query,
        generate_answer
    ])

    graph_builder.add_node("general_answer", general_answer)
    graph_builder.add_edge("general_answer", END)

    graph_builder.add_conditional_edges(
        "classify_question",
        lambda s: s["branch"],
        {
            "data_query": "get_tables",
            "general_qa": "general_answer"
        }
    )

    conn = sqlite3.connect(str(CHECKPOINT_DB_PATH), check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    graph = graph_builder.compile(checkpointer=checkpointer)

    if not os.path.exists(THREAD_COUNTER_FILE):
        with open(THREAD_COUNTER_FILE, "w") as f:
            json.dump({"counter": 1}, f)


def get_next_thread_id() -> str:
    """Get the next available thread ID, increment the counter."""
    with open(THREAD_COUNTER_FILE, "r+") as f:
        data = json.load(f)
        thread_id = str(data["counter"])
        data["counter"] += 1
        f.seek(0)
        json.dump(data, f)
        f.truncate()
    return thread_id


def list_chats() -> List[str]:
    """List all created chat IDs."""
    with open(THREAD_COUNTER_FILE, "r") as f:
        data = json.load(f)
    counter = data["counter"]
    return [str(i) for i in range(1, counter)]


def get_chat_history(chat_id: str) -> Dict:
    """Retrieve all messages from a given chat_id (thread)."""
    config = {"configurable": {"thread_id": chat_id}}

    try:
        snapshot = graph.get_state(config)
        messages = snapshot.values.get("messages", [])
    except Exception:
        return {"error": "Chat not found"}

    result = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            result.append({"type": "human", "content": msg.content})
        elif isinstance(msg, AIMessage):
            result.append({"type": "ai", "content": msg.content})
        elif isinstance(msg, SystemMessage):
            result.append({"type": "system", "content": msg.content})
    return {"messages": result}


def run_chat(question: str, chat_id: str) -> Dict:
    """Main chat execution."""
    config = {"configurable": {"thread_id": chat_id}}

    try:
        snapshot = graph.get_state(config)
        messages = snapshot.values.get("messages", [])
    except Exception:
        messages = []

    if not any(isinstance(msg, SystemMessage) for msg in messages):
        messages.insert(0, SystemMessage(
            content=(
                "You are a helpful assistant integrated into PersonalQuery — a conversational extension of the "
                "PersonalAnalytics system developed by the Human Aspects of Software Engineering Lab at the University of Zurich.\n\n"
                "PersonalAnalytics is a self-monitoring tool that tracks computer interaction data, including user input, app usage, and website visits. "
                "It also collects self-reported insights through periodic reflection questions, such as perceived productivity. "
                "All data is stored locally to protect user privacy, with optional export and obfuscation tools.\n\n"
                "PersonalQuery enhances this by offering an AI-powered interface for natural, conversational access to the collected data."
            )
        ))

    messages.append(HumanMessage(content=question))

    state: State = {
        "messages": messages,
        "question": question,
        "title": "New Chat",
        "branch": "",
        "tables": [],
        "activities": [],
        "query": "",
        "result": "",
        "answer": ""
    }

    final_state = graph.invoke(state, config)

    return {
        "answer": final_state["answer"],
        "tables": final_state["tables"],
        "activities": final_state["activities"],
        "query": final_state["query"],
        "result": final_state["result"],
    }
