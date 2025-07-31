# gclit/application/use_cases/generate_commit.py

from gclit.domain.models.commit_message import CommitContext
from gclit.domain.ports.git import GitProvider
from gclit.domain.ports.llm import LLMProvider

class GenerateCommitMessage:
    def __init__(self, llm_provider: LLMProvider, git_provider: GitProvider):
        self.llm_provider = llm_provider
        self.git_provider = git_provider

    def execute(self, lang: str = "en") -> str:
        diff = self.git_provider.get_stash_diff()
        if not diff:
            return "No staged changes to generate commit message."

        context = CommitContext(
            diff=diff,
            branch_name=self.git_provider.get_branch_name(),
            lang=lang
        )

        return self.llm_provider.generate_commit_message(context)
