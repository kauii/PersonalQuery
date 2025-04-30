import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from langchain import hub
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.prompt_values import ChatPromptValue
from langchain_openai import ChatOpenAI

from llm_registry import LLMRegistry
from schemas import QuestionType, State

load_dotenv()
output_parser = PydanticToolsParser(tools=[QuestionType])
prompt_template = hub.pull("classify_question")
prompt_template_title = hub.pull("generate_title")

APPDATA_PATH = Path(os.getenv("APPDATA", Path.home()))
CHECKPOINT_DB_PATH = APPDATA_PATH / "personal-analytics" / "chat_checkpoints.db"


def classify_chain(llm: ChatOpenAI):
    return (
            prompt_template
            | llm.with_structured_output(QuestionType)
            | (lambda parsed: parsed["questionType"])
    )


def classify_question(state: State) -> State:
    """For LangGraph Orchestration"""
    llm = LLMRegistry.get("openai")
    branch = classify_chain(llm).invoke(state)
    state['branch'] = branch
    return state


def generate_title(state: State) -> State:
    """For LangGraph Orchestration"""
    llm = LLMRegistry.get("llama31")
    prompt: ChatPromptValue = prompt_template_title.invoke({
        "question": state["question"],
        "max_characters": 15
    })

    title = llm.invoke(prompt.to_string()).content
    thread_id = state["thread_id"]

    try:
        conn = sqlite3.connect(str(CHECKPOINT_DB_PATH), check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
                    INSERT OR REPLACE INTO chat_metadata (thread_id, title)
                    VALUES (?, ?)
                """, (thread_id, title.strip()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[generate_title] Failed to persist title for thread {thread_id}: {e}")

    return state
