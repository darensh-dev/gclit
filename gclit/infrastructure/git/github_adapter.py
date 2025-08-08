# gclit/infrastructure/git/github_adapter.py

import requests
from typing import Optional
from requests.exceptions import HTTPError, RequestException

from gclit.domain.exceptions.exception import GitProviderException
from gclit.domain.models.pull_request import PullRequestInfo
from gclit.infrastructure.git.base_git_adapter import BaseGitAdapter


class GitHubAdapter(BaseGitAdapter):
    def __init__(self, token: str, repo: str):
        self.token = token
        self.repo = repo
        self.api_url = f"https://api.github.com/repos/{self.repo}"

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json"
        }

    def _handle_http_error(self, response: requests.Response, context: str = ""):
        try:
            response.raise_for_status()
        except HTTPError as e:
            try:
                data = response.json()
                message = data.get("message", response.text)
                errors = data.get("errors", [])
                details = "\n".join(f"- {err.get('message') or str(err)}" for err in errors) if errors else ""
            except Exception:
                message = response.text
                details = ""

            full_message = f"{context} - GitHub API error {response.status_code}: {message}"
            if details:
                full_message += f"\n{details}"

            raise GitProviderException(full_message) from e
        except RequestException as e:
            raise GitProviderException(f"{context} - Error de red al conectar con GitHub.") from e

    def _find_existing_pr(self, from_branch: str, to_branch: str) -> Optional[int]:
        """Verifica si ya hay un PR abierto desde from_branch a to_branch"""
        url = f"{self.api_url}/pulls"
        owner = self.repo.split("/")[0]
        params = {
            "state": "open",
            "head": f"{owner}:{from_branch}",
            "base": to_branch
        }
        res = requests.get(url, headers=self._headers(), params=params)
        self._handle_http_error(res, "Al buscar PR existente")
        prs = res.json()
        if prs:
            return prs[0]["number"]
        return None

    def get_pr_diff_by_number(self, pr_number: int) -> PullRequestInfo:
        url = f"{self.api_url}/pulls/{pr_number}"
        res = requests.get(url, headers=self._headers())
        self._handle_http_error(res, f"Al obtener PR #{pr_number}")
        data = res.json()
        return PullRequestInfo(
            pr_number=pr_number,
            from_branch=data["head"]["ref"],
            to_branch=data["base"]["ref"]
        )

    def update_pr(self, pr_number: int, title: str, body: str) -> None:
        url = f"{self.api_url}/pulls/{pr_number}"
        res = requests.patch(url, headers=self._headers(), json={"title": title, "body": body})
        self._handle_http_error(res, f"Al actualizar PR #{pr_number}")

    def create_pr(self, from_branch: str, to_branch: str, title: str, body: str) -> str:
        existing_pr = self._find_existing_pr(from_branch, to_branch)
        if existing_pr:
            raise GitProviderException(
                f"Ya existe un Pull Request abierto de `{from_branch}` hacia `{to_branch}` (PR #{existing_pr}).\n"
                f"Puedes usar `gclit pr --pr {existing_pr}` para actualizarlo."
            )

        res = requests.post(
            f"{self.api_url}/pulls",
            headers=self._headers(),
            json={"head": from_branch, "base": to_branch, "title": title, "body": body}
        )
        self._handle_http_error(res, f"Al crear PR de `{from_branch}` a `{to_branch}`")
        return res.json()["html_url"]
