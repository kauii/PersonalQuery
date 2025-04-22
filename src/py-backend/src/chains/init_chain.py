from dotenv import load_dotenv
from langchain import hub
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.prompt_values import ChatPromptValue
from langchain_openai import ChatOpenAI

from llm_registry import LLMRegistry
from schemas import QuestionType, State

load_dotenv()
output_parser = PydanticToolsParser(tools=[QuestionType])
prompt_template = hub.pull("classify_question")
prompt_template_title = hub.pull("generate_title")


def classify_chain(llm: ChatOpenAI):
    return (
            prompt_template
            | llm.with_structured_output(QuestionType)
            | (lambda parsed: parsed["questionType"])
    )


def classify_question(state: State) -> State:
    """For LangGraph Orchestration"""
    llm = LLMRegistry.get("openai")
    branch = classify_chain(llm).invoke(state)
    state['branch'] = branch
    return state


def generate_title(state: State) -> State:
    """For LangGraph Orchestration"""
    llm = LLMRegistry.get("llama31")
    prompt: ChatPromptValue = prompt_template_title.invoke({
        "question": state["question"],
    })

    state["title"] = llm.invoke(prompt.to_string()).content
    return state
