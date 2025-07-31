# gclit/application/use_cases/generate_pr_docs.py

from gclit.domain.models.common import Lang
from gclit.domain.ports.llm import LLMProvider
from gclit.domain.models.pull_request import PullRequestContext, PullRequestInfo
from gclit.domain.ports.git import GitProvider


class GeneratePullRequestDocs:
    def __init__(self, llm_provider: LLMProvider, git_provider: GitProvider):
        self.llm_provider = llm_provider
        self.git_provider = git_provider

    # TODO: tipar respuesta
    def execute(self, from_branch: str = None, to_branch: str = None, pr_number: int = None, lang: Lang = "en") -> dict:
        if pr_number is not None:
            pr_data: PullRequestInfo = self.git_provider.get_pr_diff_by_number(pr_number)
            from_branch = pr_data.from_branch
            to_branch = pr_data.to_branch

        diff = self.git_provider.get_branch_diff(from_branch, to_branch)

        if not diff:
            # TODO: estructurar respuesta
            return None

        context = PullRequestContext(
            diff=diff,
            from_branch=from_branch,
            to_branch=to_branch,
            lang=lang
        )

        result = self.llm_provider.generate_pr_documentation(context)

        if pr_number is not None:
            self.git_provider.update_pr(pr_number, title=result["title"], body=result["body"])
        else:
            self.git_provider.create_pr(
                from_branch=from_branch,
                to_branch=to_branch,
                title=result["title"],
                body=result["body"]
            )

        return {
            "title": result["title"],
            "body": result["body"]
        }
