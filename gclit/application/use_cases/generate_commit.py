# application/use_cases/generate_commit.py
from gclit.domain.models.commit_message import CommitContext
from gclit.infrastructure.git.git_diff_provider import get_git_diff
from gclit.config.settings import settings

def generate_commit_message(lang: str = "en") -> str:
    diff = get_git_diff()
    if not diff:
        return "No staged changes to generate commit message."

    context = CommitContext(
        diff=diff,
        branch_name=get_branch_name(),
        lang=lang
    )

    return settings.llm_provider.generate_commit_message(context)

def get_branch_name() -> str:
    import subprocess
    result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
    return result.stdout.strip()
