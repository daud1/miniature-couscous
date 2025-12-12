import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    TEMPERATURE = 0.9

    MAX_RETRIES = 3

    PROVIDER_MODELS = {
        "Groq": [
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile",
            "mixtral-8x7b-32768",
        ],
        "OpenAI": [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
        ],
        "Anthropic": [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-haiku-20240307",
        ],
    }

    PROVIDER_API_KEYS = {
        "Groq": GROQ_API_KEY,
        "OpenAI": OPENAI_API_KEY,
        "Anthropic": ANTHROPIC_API_KEY,
    }

    @staticmethod
    def get_available_providers():
        available = []
        for provider, api_key in Settings.PROVIDER_API_KEYS.items():
            if api_key:
                available.append(provider)
        return available


settings = Settings()
