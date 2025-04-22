from typing import Literal

from dotenv import load_dotenv
from langchain import hub
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI

from llm_registry import LLMRegistry
from schemas import QuestionType, State

load_dotenv()
output_parser = PydanticToolsParser(tools=[QuestionType])
prompt_template = hub.pull("classify_question")


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
