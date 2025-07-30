# gclit/application/use_cases/generate_pr_docs.py

from gclit.domain.services.llm import LLMProvider
from gclit.domain.models.pull_request import PullRequestContext
import subprocess

class GeneratePullRequestDocs:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def execute(self, branch_from: str, branch_to: str, lang: str = "en") -> dict:
        diff = self._get_diff_between_branches(branch_from, branch_to)

        context = PullRequestContext(
            diff=diff,
            branch_from=branch_from,
            branch_to=branch_to,
            lang=lang
        )

        result = self.llm_provider.generate_pr_documentation(context)
        return {
            "title": result["title"],
            "body": result["body"]
        }

    def _get_diff_between_branches(self, from_branch: str, to_branch: str) -> str:
        result = subprocess.run(
            ["git", "diff", f"{to_branch}...{from_branch}"],
            capture_output=True, text=True
        )
        return result.stdout
