# gclit/infrastructure/git/base_git_adapter.py
import subprocess
from gclit.domain.ports.git import GitProvider

class BaseGitAdapter(GitProvider):
    def get_branch_name(self) -> str:
        result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
        return result.stdout.strip()

    def get_stash_diff(self) -> str:
        result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)
        return result.stdout

    def get_branch_diff(self, from_branch: str, to_branch: str) -> str:
        result = subprocess.run(["git", "diff", f"{to_branch}..{from_branch}"], capture_output=True, text=True)
        return result.stdout

    