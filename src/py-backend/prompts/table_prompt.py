from langchain import hub
from dotenv import load_dotenv
from src.schemas import State

load_dotenv()

prompt_template = hub.pull("get_relevant_tables")


def create_get_table_prompt(state: State):
    prompt = prompt_template.invoke(
        {
            "question": state["question"],
        }
    )
    return prompt

create_get_table_prompt({"question": "Please review my session yesterday."})
