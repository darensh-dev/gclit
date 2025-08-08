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

    def get_git_provier(self) -> LLMProvider:
        result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True)
        url = result.stdout.strip()
        if "github.com" in url:
            # Soporta formatos SSH y HTTPS
            token = settings.github.token
            match = re.search(r"(github\.com[:/])(.+?)(\.git)?$", url)

            if not match:
                raise GitProviderException("No se pudo extraer el repo de GitHub")
            repo = match.group(2)
            return GitHubAdapter(token=token, repo=repo)

        elif "dev.azure.com" in url:
            match = re.search(r"dev\.azure\.com/([^/]+)/([^/]+)/_git/([^/]+)", url)
            token = settings.azure_devops.token

            if not match:
                raise GitProviderException("No se pudo extraer info de Azure DevOps")
            organization, project, repo = match.groups()
            return AzureDevOpsAdapter(
                token=token,
                organization=organization,
                project=project,
                repo=repo
            )

        else:
            raise GitProviderException("Proveedor Git no reconocido en la URL del repo")


container = Container()
