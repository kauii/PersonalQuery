import os
from typing import Dict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langgraph.graph import START, StateGraph

from chains.activity_chain import extract_activities
from chains.answer_chain import generate_answer
from chains.query_chain import write_query, execute_query
from chains.table_chain import get_tables
from chat_store import save_memory, load_memory
from schemas import State

load_dotenv()

chat_sessions: Dict[str, ConversationBufferMemory] = {}


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


def get_or_create_memory(chat_id: str) -> ConversationBufferMemory:
    if chat_id not in chat_sessions:
        chat_sessions[chat_id] = load_memory(chat_id)
    return chat_sessions[chat_id]


def run_chat(question: str, chat_id: str) -> Dict:
    memory = get_or_create_memory(chat_id)
    memory.chat_memory.add_user_message(question)

    graph_builder = StateGraph(State).add_sequence([
            get_tables,
            extract_activities,
            write_query,
            execute_query,
            generate_answer
        ])

    graph_builder.add_edge(START, "get_tables")
    graph = graph_builder.compile()

    state: State = {
        "llm_openai": llm_openai,
        "llm_private": llm_llama31,
        "question": question,
        "tables": [],
        "activities": [],
        "query": "",
        "result": "",
        "answer": ""
    }

    final_state = graph.invoke(state)

    response = {
        "answer": final_state["answer"],
        "tables": final_state["tables"],
        "activities": final_state["activities"],
        "query": final_state["query"],
        "result": final_state["result"],
    }

    memory.chat_memory.messages.append(
        AIMessage(
            content=response["answer"],
            additional_kwargs={"meta": {
                "tables": response["tables"],
                "activities": response["activities"],
                "query": response["query"],
                "result": response["result"]
            }}
        )
    )

    save_memory(chat_id, memory)

    return response
