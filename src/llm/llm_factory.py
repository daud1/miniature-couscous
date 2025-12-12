from src.common.custom_exception import CustomException
from src.config.settings import settings
from src.llm.anthropic_client import get_anthropic_llm
from src.llm.groq_client import get_groq_llm
from src.llm.openai_client import get_openai_llm


def get_llm(provider: str, model: str):
    if provider not in settings.PROVIDER_MODELS:
        raise CustomException(f"Unknown provider: {provider}", None)

    if model not in settings.PROVIDER_MODELS[provider]:
        raise CustomException(f"Unknown model {model} for provider {provider}", None)

    if provider == "Groq":
        if not settings.GROQ_API_KEY:
            raise CustomException("GROQ_API_KEY not set in environment", None)
        return get_groq_llm(model)

    elif provider == "OpenAI":
        if not settings.OPENAI_API_KEY:
            raise CustomException("OPENAI_API_KEY not set in environment", None)
        return get_openai_llm(model)

    elif provider == "Anthropic":
        if not settings.ANTHROPIC_API_KEY:
            raise CustomException("ANTHROPIC_API_KEY not set in environment", None)
        return get_anthropic_llm(model)

    else:
        raise CustomException(f"Provider {provider} not implemented", None)

