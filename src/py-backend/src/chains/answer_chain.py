from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompt_values import ChatPromptValue

from llm_registry import LLMRegistry
from schemas import State
from langchain_openai import ChatOpenAI

load_dotenv()
prompt_template = hub.pull("generate_answer")
prompt_template_general = hub.pull("general_answer")


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
    llm = LLMRegistry.get("llama31")
    prompt: ChatPromptValue = prompt_template.invoke({
        "question": state["question"],
        "result": state["result"]
    })

    state["answer"] = llm.invoke(prompt.to_string()).content
    return state


def general_answer(state: State) -> State:
    llm = LLMRegistry.get("llama31")
    prompt: ChatPromptValue = prompt_template_general.invoke({
        "question": state["question"]
    })
    state["answer"] = llm.invoke(prompt.to_string()).content
    return state
