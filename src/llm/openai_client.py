from langchain_openai import ChatOpenAI

from src.config.settings import settings


def get_openai_llm(model: str):
    return ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model=model,
        temperature=settings.TEMPERATURE,
    )

