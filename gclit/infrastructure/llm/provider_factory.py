# infrastructure/llm/provider_factory.py

from gclit.domain.services.llm import LLMProvider
from gclit.config.settings import settings

from gclit.infrastructure.llm.openai_provider import OpenAIProvider
# from infrastructure.llm.claude_provider import ClaudeProvider
# from infrastructure.llm.local_provider import LocalProvider


def get_llm_provider() -> LLMProvider:
    provider = settings.provider.lower()

    if provider == "openai":
        return OpenAIProvider(
            model=settings.model,
            api_key=settings.providers.openai.api_key
        )

    elif provider == "claude":
        # Implementar ClaudeProvider y descomentar
        raise NotImplementedError("ClaudeProvider not implemented yet")

    elif provider == "local":
        # Implementar LocalProvider para modelos locales como LM Studio, LLaMA, etc.
        raise NotImplementedError("LocalProvider not implemented yet")

    else:
        raise ValueError(f"❌ Unsupported LLM provider: {provider}")
