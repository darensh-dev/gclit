# gclit/application/use_cases/generate_pr_docs.py

from gclit.domain.models.common import Lang
from gclit.domain.ports.llm import LLMProvider
from gclit.domain.models.pull_request import PullRequestContext
from gclit.domain.ports.git import GitProvider


class GeneratePullRequestDocs:
    def __init__(self, llm_provider: LLMProvider, git_repo: GitProvider):
        self.llm_provider = llm_provider
        self.git_repo = git_repo

    def execute(self, branch_from: str = None, branch_to: str = None, pr_number: int = None, lang: Lang = "en") -> dict:
        if pr_number is not None:
            pr_data = self.git_repo.get_pull_request_data(pr_number)
            branch_from = pr_data.branch_from
            branch_to = pr_data.branch_to

        diff = self.git_repo.get_diff(branch_from, branch_to)

        context = PullRequestContext(
            diff=diff,
            branch_from=branch_from,
            branch_to=branch_to,
            lang=lang
        )

        result = self.llm_provider.generate_pr_documentation(context)

        if pr_number is not None:
            self.git_repo.update_pull_request(pr_number, title=result["title"], body=result["body"])

        return {
            "title": result["title"],
            "body": result["body"]
        }
