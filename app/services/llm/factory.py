import os
from app.services.llm.base import LLMProvider
from app.services.llm.gemini import GeminiProvider


class LLMFactory:
    @staticmethod
    def get_provider() -> LLMProvider:
        provider_type = os.getenv("LLM_PROVIDER", "gemini")
        if provider_type == "gemini":
            return GeminiProvider()
        raise ValueError(f"Unsupported provider type: {provider_type}")
