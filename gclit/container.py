# gclit/container.py

from gclit.config.settings import settings
from gclit.infrastructure.llm.openai_provider import OpenAIProvider
from gclit.domain.services.llm import LLMProvider

class Container:
    def __init__(self):
        self._llm_provider = None

    def get_llm_provider(self) -> LLMProvider:
        if self._llm_provider is None:
            provider = settings.provider.lower()
            if provider == "openai":
                self._llm_provider = OpenAIProvider(
                    model=settings.model,
                    api_key=settings.providers.openai.api_key
                )
            # Agrega aquí otros proveedores...
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
        return self._llm_provider

container = Container()
