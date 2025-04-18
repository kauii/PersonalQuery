from dotenv import load_dotenv
from langchain import hub
from langchain_community.tools import QuerySQLDatabaseTool
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from db.database import get_db
from src.schemas import Table, State, QueryOutput

load_dotenv()
db = get_db()

main_template = hub.pull("langchain-ai/sql-query-system-prompt")

esr_template = hub.pull("experience_sampling_responses")
ud_template = hub.pull("usage_data")
ui_template = hub.pull("user_input")
wa_template = hub.pull("window_activity")


def get_custom_table_info(state: State):
    prompt_parts = []
    tables = state["tables"]
    activities = state.get("activities", None)
    for table in tables:
        template = None
        template_input = {"table_info": db.get_table_info([table])}
        if table == "experience_sampling_responses":
            template = esr_template
        elif table == "usage_data":
            template = ud_template
        elif table == "user_input":
            template = ui_template
        elif table == "window_activity":
            template = wa_template
            if activities:
                template_input["activities"] = activities
        if template:
            result = template.invoke(template_input)
            prompt_parts.append(result.to_string())
    return "\n\n---\n\n".join(prompt_parts)



def query_chain(llm: ChatOpenAI):

    return (
            RunnableLambda(lambda state: main_template.invoke({
                "dialect": db.dialect,
                "top_k": 30,
                "table_info": get_custom_table_info(state) if state["tables"] else db.get_table_info(),
                "input": state["question"]
            }))
            | llm.with_structured_output(QueryOutput)
            | (lambda parsed: parsed["query"])
    )


def write_query(state: State) -> State:
    """For LangGraph Orchestration"""
    llm = state['llm_openai']
    query = query_chain(llm).invoke(state)
    state['query'] = query
    return state


def is_safe_query(query: str) -> bool:
    """Check if the SQL query is read-only."""
    lowered = query.lower()
    unsafe_keywords = ["insert", "update", "delete", "drop", "alter", "create", "truncate"]
    return not any(keyword in lowered for keyword in unsafe_keywords)


def execute_query_old(state: State) -> str:
    if not is_safe_query(state["query"]):
        raise ValueError("Unsafe query detected. Aborting execution.")
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    result = execute_query_tool.invoke(state["query"])
    return result


def execute_query(state: State) -> State:
    if not is_safe_query(state["query"]):
        raise ValueError("Unsafe query detected. Aborting execution.")
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    result = db._execute(state["query"])

    state["result"] = format_result_as_markdown(result)
    return state


def format_result_as_markdown(result: list[dict]) -> str:
    if not result:
        return "No results found"
    headers = result[0].keys()
    rows = [list(row.values()) for row in result]

    # Create Markdown table
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")

    return "\n".join(lines)
