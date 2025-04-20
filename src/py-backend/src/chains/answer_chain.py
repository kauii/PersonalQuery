from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompt_values import ChatPromptValue

from src.schemas import State
from langchain_openai import ChatOpenAI

load_dotenv()
prompt_template = hub.pull("generate_answer")


def answer_chain(llm: ChatOpenAI, state: State):
    """Answer question using retrieved information as context."""
    prompt = (
        "Given the following user question, corresponding SQL query, "
        "and SQL result, answer the user question.\n\n"
        f'Question: {state["question"]}\n'
        f'SQL Query: {state["query"]}\n'
        f'SQL Result: {state["result"]}'
    )
    response = llm.invoke(prompt)
    return response.content


def generate_answer(state: State) -> State:
    """For LangGraph Orchestration"""
    llm = state["llm_private"]
    prompt: ChatPromptValue = prompt_template.invoke({
        "question": state["question"],
        "result": state["result"]
    })


    state["answer"] = llm.invoke(prompt.to_string()).content
    return state
