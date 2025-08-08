# gclit/application/use_cases/generate_commit.py

from typing import Any, Dict
from gclit.domain.exceptions.exception import GitProviderException
from gclit.domain.models.commit_message import CommitContext
from gclit.domain.models.common import Lang
from gclit.domain.ports.git import GitProvider
from gclit.domain.ports.llm import LLMProvider


class GenerateCommitMessage:
    def __init__(self, llm_provider: LLMProvider, git_provider: GitProvider):
        self.llm_provider = llm_provider
        self.git_provider = git_provider

    def execute(self, lang: Lang = "en") -> str:
        """
        Genera un mensaje de commit y opcionalmente lo aplica
        """
        diff = self.git_provider.get_stash_diff()
        if not diff:
            raise GitProviderException("No staged changes to generate commit message.")

        commit_history = self.git_provider.get_recent_commits(limit=5)

        context = CommitContext(
            diff=diff,
            branch_name=self.git_provider.get_branch_name(),
            commit_history=commit_history,
            lang=lang,
        )

        commit_message = self.llm_provider.generate_commit_message(context)
        return commit_message

    def apply_commit(self, message: str) -> str:
        """Aplica un commit con el mensaje dado"""
        return self.git_provider.create_commit(message)
