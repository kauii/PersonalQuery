from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from db.database import get_db
from langgraph.graph import START, StateGraph

from src.chains.activity_chain import extract_activities
from src.chains.answer_chain import generate_answer
from src.chains.query_chain import write_query, execute_query
from src.chains.table_chain import get_tables
from src.schemas import State

load_dotenv()

db = get_db()

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

state: State = {
    "llm_openai": llm_openai,
    "llm_private": llm_llama31,
    "question": "Was I actually productive during the sessions where I rated myself as productive? on March 25th, 2025",
    "tables": [],
    "activities": [],
    "query": "",
    "result": "",
    "answer": ""
}

final_state = graph.invoke(state)
print(final_state["query"])
print(final_state["activities"])
print(final_state["answer"])
