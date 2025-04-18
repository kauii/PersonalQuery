from langchain import hub
from typing_extensions import Annotated, TypedDict
from dotenv import load_dotenv
from src.schemas import State
from langchain_community.utilities import SQLDatabase

load_dotenv()

query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")


class QueryOutput(TypedDict):
    """Generated SQL query"""
    query: Annotated[str, ..., "Syntactically valid SQL query."]


def create_query_prompt_old(state: State, db: SQLDatabase):
    """Generate SQL query to fetch information."""

    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 10,
            "table_info": db.get_table_info(),
            "input": state["question"],
        }
    )

    return prompt
