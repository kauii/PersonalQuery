import os
import sqlite3
import uuid
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, AIMessageChunk
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.graph import CompiledGraph

from chains.activity_chain import extract_activities
from chains.answer_chain import generate_answer, general_answer
from chains.query_chain import write_query, execute_query
from chains.table_chain import get_tables
from chains.init_chain import classify_question, generate_title
from chains.context_chain import give_context
from helper.chat_utils import title_exists
from helper.db_modification import update_sessions_from_usage_data, add_window_activity_durations
from schemas import State
from llm_registry import LLMRegistry

APPDATA_PATH = Path(os.getenv("APPDATA", Path.home()))
CHECKPOINT_DB_PATH = APPDATA_PATH / "personal-analytics" / "chat_checkpoints.db"
DB_PATH = APPDATA_PATH / "personal-analytics" / "database.sqlite"

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
    graph_builder.add_node("generate_title", generate_title)

    graph_builder.add_edge(START, "classify_question")

    graph_builder.add_sequence([
        give_context,
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
        lambda s: (
            "generate_title" if s["branch"] == "data_query" and not s.get("title_exist", False)
            else "give_context" if s["branch"] == "data_query"
            else "general_answer"
        ),
        {
            "generate_title": "generate_title",
            "give_context": "give_context",
            "general_answer": "general_answer"
        }
    )

    graph_builder.add_edge("generate_title", "give_context")

    conn = sqlite3.connect(str(CHECKPOINT_DB_PATH), check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    graph = graph_builder.compile(checkpointer=checkpointer)

    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_metadata (
            thread_id TEXT PRIMARY KEY,
            title TEXT,
            last_activity TEXT
        )
    """)

    update_sessions_from_usage_data(DB_PATH)
    add_window_activity_durations(DB_PATH)


def run_chat(question: str, chat_id: str) -> Dict:
    """Main chat execution."""
    config = {"configurable": {"thread_id": chat_id}}

    try:
        snapshot = graph.get_state(config)
        messages = snapshot.values.get("messages", [])
        metadata = snapshot.values.get("metadata", [])
    except Exception:
        messages = []
        metadata = []

    current_time = datetime.now().isoformat()

    if not any(isinstance(msg, SystemMessage) for msg in messages):
        messages.insert(0, SystemMessage(
            content=(
                "You are a helpful assistant integrated into PersonalQuery — a conversational extension of the "
                "PersonalAnalytics system developed by the Human Aspects of Software Engineering Lab at the University of Zurich.\n\n"
                "PersonalAnalytics is a self-monitoring tool that tracks computer interaction data, including user input, app usage, and website visits. "
                "It also collects self-reported insights through periodic reflection questions, such as perceived productivity. "
                "All data is stored locally to protect user privacy, with optional export and obfuscation tools.\n\n"
                "PersonalQuery enhances this by offering an AI-powered interface for natural, conversational access to the collected data."
                f"\n\nCurrent time: {current_time}"
            )
        ))

    messages.append(HumanMessage(content=question))

    state: State = {
        "thread_id": chat_id,
        "messages": messages,
        "question": question,
        "title_exist": title_exists(chat_id),
        "branch": "",
        "current_time": current_time,
        "tables": [],
        "activities": [],
        "query": "",
        "raw_result": "",
        "result": [],
        "answer": "",
    }

    final_state = graph.invoke(state, config)

    now = datetime.now(UTC).isoformat()
    conn = sqlite3.connect(str(CHECKPOINT_DB_PATH), check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
            INSERT INTO chat_metadata (thread_id, last_activity)
            VALUES (?, ?)
            ON CONFLICT(thread_id) DO UPDATE SET last_activity = excluded.last_activity
        """, (chat_id, now))
    conn.commit()
    conn.close()

    msg_id = str(uuid.uuid4())
    state["messages"].append(AIMessage(
        content=state["answer"],
        additional_kwargs={
            "meta": {
                "tables": state["tables"],
                "activities": state["activities"],
                "query": state["query"],
                "result": state["result"]
            },
            "message_id": msg_id
        }
    ))

    return {
        "answer": final_state["answer"],
        "tables": final_state["tables"],
        "activities": final_state["activities"],
        "query": final_state["query"],
        "result": final_state["raw_result"],
    }


def get_chat_history(chat_id: str) -> Dict:
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
            print({"type": "ai", "content": msg.content, "additional_kwargs": msg.additional_kwargs})
            result.append({"type": "ai", "content": msg.content, "additional_kwargs": msg.additional_kwargs})
        elif isinstance(msg, SystemMessage):
            result.append({"type": "system", "content": msg.content})
        elif isinstance(msg, AIMessageChunk):
            print(msg)

    return {"messages": result}
