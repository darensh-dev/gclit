# gclit/infrastructure/git/git_repository.py

import subprocess
from gclit.domain.ports.git_port import GitPort

class GitHubAdapter(GitPort):
    def get_branch_diff(self, branch_from: str, branch_to: str) -> str:
        result = subprocess.run(
            ["git", "diff", f"{branch_to}...{branch_from}"],
            capture_output=True, text=True
        )
        return result.stdout.strip()

    def get_current_branch(self) -> str:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True
        )
        return result.stdout.strip()

    def get_remote_url(self) -> str:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True, text=True
        )
        return result.stdout.strip()

    # Estos métodos requieren integración con GitHub o Azure DevOps
    def get_pr_diff_by_number(self, pr_number: int) -> str:
        raise NotImplementedError("This method must be implemented using GitHub or Azure DevOps API.")

    def update_pr(self, pr_number: int, title: str, body: str) -> None:
        raise NotImplementedError("This method must be implemented using GitHub or Azure DevOps API.")

    def create_pr(self, from_branch: str, to_branch: str, title: str, body: str) -> str:
        raise NotImplementedError("This method must be implemented using GitHub or Azure DevOps API.")
