
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage

from llm_registry import LLMRegistry
from schemas import State, Question

load_dotenv()


def give_context(state: State) -> State:
    system_prompt = (
        "You are a helpful assistant that rewrites the user's most recent question to make it self-contained and unambiguous,"
        "but only if necessary.\n\n"
        "Use the previous messages for context.\n"
        "- Resolve vague time expressions using the current time (ISO-format): {current_time}\n"
        "- Clarify pronouns or references like 'that', 'them', or 'on that day'\n"
        "- Only rewrite the most recent question, and only as much as needed\n"
        "- Do not change meaning or tone\n"
        "- If the question is already clear and fully self-contained, leave it unchanged\n"
        "- Return only the (rewritten) question"
    ).format(current_time=state['current_time'])
    llm = LLMRegistry.get("openai")
    messages = state['messages']
    temp_messages = messages.copy()

    if temp_messages and isinstance(temp_messages[0], SystemMessage):
        temp_messages[0] = SystemMessage(content=system_prompt)
    else:
        temp_messages.insert(0, SystemMessage(content=system_prompt))

    enriched_question = llm.with_structured_output(Question).invoke(temp_messages)
    print(enriched_question)
    state['question'] = enriched_question

    return state
