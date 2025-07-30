# gclit/infrastructure/git/github_repository.py

import requests
from gclit.domain.ports.git_service import GitProvider
from gclit.domain.models.pull_request import PullRequestInfo

class GitHubRepository(GitProvider):
    def __init__(self, token: str, repo: str):
        self.token = token
        self.repo = repo  # Ejemplo: "usuario/repositorio"
        self.api_url = f"https://api.github.com/repos/{self.repo}"

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json"}

    def get_diff(self, branch_from: str, branch_to: str) -> str:
        import subprocess
        result = subprocess.run(["git", "diff", f"{branch_to}..{branch_from}"], capture_output=True, text=True)
        return result.stdout

    def get_pull_request_data(self, pr_number: int) -> PullRequestInfo:
        res = requests.get(f"{self.api_url}/pulls/{pr_number}", headers=self._headers())
        res.raise_for_status()
        data = res.json()
        return PullRequestInfo(
            pr_number=pr_number,
            branch_from=data["head"]["ref"],
            branch_to=data["base"]["ref"]
        )

    def update_pull_request(self, pr_number: int, title: str, body: str) -> None:
        requests.patch(
            f"{self.api_url}/pulls/{pr_number}",
            headers=self._headers(),
            json={"title": title, "body": body}
        ).raise_for_status()

    def create_pull_request(self, from_branch: str, to_branch: str, title: str, body: str) -> str:
        res = requests.post(
            f"{self.api_url}/pulls",
            headers=self._headers(),
            json={"head": from_branch, "base": to_branch, "title": title, "body": body}
        )
        res.raise_for_status()
        return res.json()["html_url"]
