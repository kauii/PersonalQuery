import uuid

from dotenv import load_dotenv
from langchain import hub
from langchain_core.messages import AIMessage, AIMessageChunk
from langchain_core.prompt_values import ChatPromptValue

from llm_registry import LLMRegistry
from schemas import State
from langchain_openai import ChatOpenAI

load_dotenv()
prompt_template_partial = hub.pull("partial_answer")
prompt_template_summarize = hub.pull("summarize_answers")

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
    llm = LLMRegistry.get("openai")
    messages = state["messages"]

    if len(state["result"]) == 1:
        prompt: ChatPromptValue = prompt_template.invoke({
            "question": state["question"],
            "result": state["result"],
            "current_time": state["current_time"]
        })
        response = llm.invoke(prompt.to_string()).content
    else:
        summaries = []

        for i, chunk_markdown in enumerate(state["result"]):
            prompt: ChatPromptValue = prompt_template_partial.invoke({
                "question": state["question"],
                "result": chunk_markdown
            })
            response = llm.invoke(prompt).content
            summaries.append(response)
            messages.append(AIMessageChunk(content=response))

        joined_summaries = "\n\n".join(
            f"Chunk {i + 1}:\n{summary}" for i, summary in enumerate(summaries)
        )

        prompt: ChatPromptValue = prompt_template_summarize.invoke({
            "question": state["question"],
            "summaries": joined_summaries,
        })
        response = llm.invoke(prompt).content

    state["answer"] = response

    messages.append(AIMessage(
        content=response,
        additional_kwargs={
            "meta": {
                "tables": state["tables"],
                "activities": state["activities"],
                "query": state["query"],
                "result": state["raw_result"]
            }
        }
    ))
    return state


def general_answer(state: State) -> State:
    llm = LLMRegistry.get("openai")
    messages = state["messages"]
    response = llm.invoke(messages).content
    state["answer"] = response
    messages.append(AIMessage(content=response))
    return state
