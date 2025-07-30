# application/use_cases/generate_pr_docs.py
from gclit.config.settings import settings
from gclit.domain.models.pull_request import PullRequestContext
from gclit.infrastructure.llm.provider_factory import get_llm_provider
from gclit.infrastructure.git.git_diff_provider import get_git_diff

def generate_pull_request_docs(branch_from: str, branch_to: str, lang: str = None) -> dict:
    diff = get_git_diff(branch_from, branch_to)
    if not diff:
        return {"title": "No changes detected", "body": ""}

    context = PullRequestContext(
        diff=diff,
        branch_from=branch_from,
        branch_to=branch_to,
        lang=lang or settings.lang
    )

    llm = get_llm_provider()
    return llm.generate_pr_documentation(context)
