from langchain_openai import ChatOpenAI


class LLMRegistry:
    _llms: dict[str, ChatOpenAI] = {}

    @classmethod
    def register(cls, name: str, llm: ChatOpenAI):
        cls._llms[name] = llm

    @classmethod
    def get(cls, name: str) -> ChatOpenAI:
        if name not in cls._llms:
            raise ValueError(f"LLM '{name}' not registered.")
        return cls._llms[name]
