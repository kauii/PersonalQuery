import os
import sqlite3
from pathlib import Path
from typing import Dict, List
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph.graph import CompiledGraph

APPDATA_PATH = Path(os.getenv("APPDATA", Path.home()))
CHECKPOINT_DB_PATH = APPDATA_PATH / "personal-query" / "chat_checkpoints.db"


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


def give_correct_step(current_node: str, branch: str, title_exist: bool = False) -> str:
    """Predict the next logical step in the workflow based on branch and current node."""
    if branch != "data_query":
        return "generate_answer"

    data_query_map = {
        "classify_question": "generate_title" if not title_exist else "give_context",
        "generate_title": "give_context",
        "give_context": "get_tables",
        "get_tables": "extract_activities",
        "extract_activities": "write_query",
        "write_query": "execute_query",
        "execute_query": "generate_answer"
    }

    return data_query_map.get(current_node, current_node)
