from typing import List

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Annotated


class State(TypedDict):
    llm_openai: ChatOpenAI
    llm_private: ChatOpenAI
    question: str
    tables: List[str]
    activities: List[str]
    query: str
    result: str
    answer: str


class QueryOutput(TypedDict):
    """Generated SQL query"""
    query: Annotated[str, ..., "Syntactically valid SQL query."]


class Table(BaseModel):
    """Table in SQL database."""
    name: str = Field(description="Name of table in SQL database.")


class Activity(BaseModel):
    """Relevant activity label from activity column in window_activity."""
    name: str = Field(description="Activity label to use in SQL filtering.")
