# gclit/infrastructure/git/github_adapter.py

import requests
from gclit.domain.exceptions.exception import GitProviderException
from gclit.domain.models.pull_request import PullRequestInfo
from gclit.infrastructure.git.base_git_adapter import BaseGitAdapter


class GitHubAdapter(BaseGitAdapter):
    def __init__(self, token: str, repo: str):
        self.token = token
        self.repo = repo
        self.api_url = f"https://api.github.com/repos/{self.repo}"

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json"}


    def get_pr_diff_by_number(self, pr_number: int) -> PullRequestInfo:
        res = requests.get(f"{self.api_url}/pulls/{pr_number}", headers=self._headers())
        res.raise_for_status()
        data = res.json()
        return PullRequestInfo(
            pr_number=pr_number,
            from_branch=data["head"]["ref"],
            to_branch=data["base"]["ref"]
        )

    def update_pr(self, pr_number: int, title: str, body: str) -> None:
        requests.patch(
            f"{self.api_url}/pulls/{pr_number}",
            headers=self._headers(),
            json={"title": title, "body": body}
        ).raise_for_status()

    def create_pr(self, from_branch: str, to_branch: str, title: str, body: str) -> str:
        res = requests.post(
            f"{self.api_url}/pulls",
            headers=self._headers(),
            json={"head": from_branch, "base": to_branch, "title": title, "body": body}
        )
        
        if res.status_code == 404:
            raise GitProviderException(f"Repositorio '{self.repo}' no encontrado o sin acceso.")
        elif res.status_code == 403:
            raise GitProviderException("Token de GitHub inválido o sin permisos suficientes.")
        
        res.raise_for_status()
        return res.json()["html_url"]
