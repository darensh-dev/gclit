# gclit/application/use_cases/generate_commit.py

from gclit.domain.models.commit_message import CommitContext
from gclit.domain.services.llm import LLMProvider

class GenerateCommitMessage:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def execute(self, lang: str = "en") -> str:
        diff = self._get_git_diff()
        if not diff:
            return "No staged changes to generate commit message."

        context = CommitContext(
            diff=diff,
            branch_name=self._get_branch_name(),
            lang=lang
        )

        return self.llm_provider.generate_commit_message(context)

    def _get_git_diff(self) -> str:
        import subprocess
        result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)
        return result.stdout

    def _get_branch_name(self) -> str:
        import subprocess
        result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
        return result.stdout.strip()
