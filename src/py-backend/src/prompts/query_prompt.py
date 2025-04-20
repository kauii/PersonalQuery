from langchain import hub
from dotenv import load_dotenv

from db.database import get_db
from src.schemas import State
from langchain_community.utilities import SQLDatabase

load_dotenv()

query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")

db = get_db()


def create_query_prompt(state: State):
    """Generate SQL query to fetch information."""
    tables_to_use = state["tables"] if state.get("tables") else db.get_usable_table_names()

    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 50,
            "table_info": db.get_table_info(tables_to_use),
            "input": state["question"],
        }
    )

    return prompt
