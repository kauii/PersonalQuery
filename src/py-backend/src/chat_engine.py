import os
import sqlite3
import uuid
from datetime import datetime, UTC
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
from chains.init_chain import classify_question, generate_title
from db_modification import update_sessions_from_usage_data, add_window_activity_durations
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
            else "get_tables" if s["branch"] == "data_query"
            else "general_answer"
        ),
        {
            "generate_title": "generate_title",
            "get_tables": "get_tables",
            "general_answer": "general_answer"
        }
    )

    graph_builder.add_edge("generate_title", "get_tables")

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



def get_next_thread_id() -> str:
    conn = sqlite3.connect(str(CHECKPOINT_DB_PATH), check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='checkpoints'
    """)
    if cursor.fetchone() is None:
        conn.close()
        return "1"

    cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
    thread_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    numeric_ids = [int(tid) for tid in thread_ids if tid.isdigit()]
    next_id = max(numeric_ids, default=0) + 1

    return str(next_id)


def list_chats() -> List[Dict[str, str]]:
    conn = sqlite3.connect(str(CHECKPOINT_DB_PATH), check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='checkpoints'
    """)
    if cursor.fetchone() is None:
        conn.close()
        return []

    cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
    thread_ids = [row[0] for row in cursor.fetchall()]

    result = []
    for tid in thread_ids:
        cursor.execute("SELECT title, last_activity FROM chat_metadata WHERE thread_id = ?", (tid,))
        row = cursor.fetchone()

        title_raw = row[0] if row else None
        title = title_raw.strip() if title_raw and title_raw.strip() else f"New Chat [{tid}]"
        last_activity = row[1] if row and row[1] else None

        result.append({
            "id": tid,
            "title": title,
            "last_activity": last_activity
        })

    conn.close()
    return result


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
            result.append({"type": "ai", "content": msg.content})
        elif isinstance(msg, SystemMessage):
            result.append({"type": "system", "content": msg.content})
    return {"messages": result}


def is_new_chat(thread_id: str) -> bool:
    conn = sqlite3.connect(str(CHECKPOINT_DB_PATH), check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='checkpoints'
    """)
    if cursor.fetchone() is None:
        conn.close()
        return True

    cursor.execute("""
        SELECT 1 FROM checkpoints
        WHERE thread_id = ?
        LIMIT 1
    """, (thread_id,))
    result = cursor.fetchone()
    conn.close()
    print("RESULT:")
    print(result)

    return result is None


def title_exists(thread_id: str) -> bool:
    conn = sqlite3.connect(str(CHECKPOINT_DB_PATH), check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title FROM chat_metadata
        WHERE thread_id = ?
        LIMIT 1
    """, (thread_id,))
    row = cursor.fetchone()
    conn.close()

    if not row or row[0] is None:
        return False

    return bool(row[0].strip())


def run_chat(question: str, chat_id: str) -> Dict:
    """Main chat execution."""
    config = {"configurable": {"thread_id": chat_id}}

    try:
        snapshot = graph.get_state(config)
        messages = snapshot.values.get("messages", [])
    except Exception:
        print("NEW")
        print("NEW")
        print("NEW")
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
        "thread_id": chat_id,
        "messages": messages,
        "question": question,
        "title_exist": title_exists(chat_id),
        "branch": "",
        "tables": [],
        "activities": [],
        "query": "",
        "result": "",
        "answer": ""
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
        "result": final_state["result"],
    }
