# gclit/container.py

import subprocess
import re

from gclit.config.settings import settings
from gclit.domain.exceptions.exception import GitProviderException, LLMProviderException
from gclit.domain.ports.git import GitProvider
from gclit.domain.ports.llm import LLMProvider

from gclit.infrastructure.llm.openai_provider import OpenAIProvider
from gclit.infrastructure.git.github_adapter import GitHubAdapter
from gclit.infrastructure.git.azure_devops_adapter import AzureDevOpsAdapter
from gclit.infrastructure.llm.openai_with_func_provider import OpenAIWithFuncProvider
from gclit.infrastructure.git.ssh_resolver import get_enhanced_git_remote


class Container:
    def __init__(self):
        self._llm_provider = None

    def get_llm_provider(self) -> LLMProvider:
        if self._llm_provider is None:
            provider = settings.provider.lower()
            if provider == "openai":
                self._llm_provider = OpenAIProvider(
                    model=settings.model,
                    api_key=settings.openai.api_key
                )

            elif provider == "openai-with-func":
                self._llm_provider = OpenAIWithFuncProvider(
                    model=settings.model,
                    api_key=settings.openai.api_key
                )

            else:
                raise LLMProviderException(f"Unsupported LLM provider: {provider}")
        return self._llm_provider

    def get_git_provier(self) -> GitProvider:
        try:
            provider_type, provider_info = get_enhanced_git_remote()

            if provider_type == 'github':
                return GitHubAdapter(
                    token=settings.github.token,
                    repo=provider_info['repo']
                )

            elif provider_type == 'azure_devops':
                return AzureDevOpsAdapter(
                    token=settings.azure_devops.token,
                    organization=provider_info['organization'],
                    project=provider_info['project'],
                    repo=provider_info['repo']
                )

            else:
                raise GitProviderException(f"Proveedor Git no soportado: {provider_type}")

        except Exception as e:
            raise GitProviderException(f"Error configurando proveedor Git: {str(e)}")


container = Container()
