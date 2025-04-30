from dotenv import load_dotenv
from langchain import hub
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from database import get_db
from llm_registry import LLMRegistry
from schemas import State, QueryOutput

load_dotenv()
db = get_db()

main_template = hub.pull("sql-query-system-prompt")
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
        db._sample_rows_in_table_info = False
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
            else:
                template_input["activities"] = ""
        if template:
            result = template.invoke(template_input)
            prompt_parts.append(result.to_string())
    return "\n\n---\n\n".join(prompt_parts)


def query_chain(llm: ChatOpenAI):
    return (
            RunnableLambda(lambda state: main_template.invoke({
                "dialect": db.dialect,
                "top_k": 100,
                "table_info": get_custom_table_info(state) if state["tables"] else db.get_table_info(),
                "input": state["question"]
            }))
            | llm.with_structured_output(QueryOutput)
            | (lambda parsed: parsed["query"])
    )


def write_query(state: State) -> State:
    """For LangGraph Orchestration"""
    llm = LLMRegistry.get("openai")
    query = query_chain(llm).invoke(state)
    state['query'] = query
    return state


def execute_query(state: State) -> State:
    result = db._execute(state["query"])

    state["result"] = format_result_as_markdown(result)
    return state


def format_result_as_markdown(result: list[dict]) -> str:
    if not result:
        return "No results found"

    headers = list(result[0].keys())
    headers = ["#"] + headers  # Add row number header

    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]

    for idx, row in enumerate(result, start=1):
        row_values = [str(idx)] + [str(value) for value in row.values()]
        lines.append("| " + " | ".join(row_values) + " |")

    return "\n".join(lines)
