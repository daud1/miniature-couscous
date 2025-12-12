from langchain_anthropic import ChatAnthropic

from src.config.settings import settings


def get_anthropic_llm(model: str):
    return ChatAnthropic(
        api_key=settings.ANTHROPIC_API_KEY,
        model=model,
        temperature=settings.TEMPERATURE,
    )

