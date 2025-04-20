from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph

from chains.activity_chain import extract_activities
from chains.answer_chain import generate_answer
from chains.query_chain import write_query, execute_query
from chains.table_chain import get_tables
from schemas import State

load_dotenv()

llm_openai = ChatOpenAI(
    model="openai-gpt-4o",
    temperature=0.0,
    base_url="http://llm.hasel.dev:20769/v1",
)

llm_llama31 = ChatOpenAI(
    model="llama31instruct",
    temperature=0.0,
    base_url="http://llm.hasel.dev:20769/v1",
)

graph_builder = StateGraph(State).add_sequence(
    [get_tables, extract_activities, write_query, execute_query, generate_answer]
)

graph_builder.add_edge(START, "get_tables")
graph = graph_builder.compile()


def run_chat(question: str) -> State:
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
    return graph.invoke(state)
