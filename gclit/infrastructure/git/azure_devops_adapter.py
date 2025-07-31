# gclit/infrastructure/git/azure_devops_adapter.py

import requests
from gclit.domain.models.pull_request import PullRequestInfo
from gclit.infrastructure.git.base_git_adapter import BaseGitAdapter


class AzureDevOpsAdapter(BaseGitAdapter):
    def __init__(self, token: str, organization: str, project: str, repo: str):
        self.token = token
        self.organization = organization
        self.project = project
        self.repo = repo
        self.api_url = f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repo}"

    def _headers(self):
        return {
            "Authorization": f"Basic {self._encode_token()}",
            "Content-Type": "application/json"
        }

    def _encode_token(self):
        import base64
        return base64.b64encode(f":{self.token}".encode()).decode()

    def get_pr_diff_by_number(self, pr_number: int) -> PullRequestInfo:
        res = requests.get(
            f"{self.api_url}/pullrequests/{pr_number}?api-version=7.1-preview.1",
            headers=self._headers()
        )
        res.raise_for_status()
        data = res.json()
        return PullRequestInfo(
            pr_number=pr_number,
            from_branch=data["sourceRefName"].replace("refs/heads/", ""),
            to_branch=data["targetRefName"].replace("refs/heads/", "")
        )

    def update_pr(self, pr_number: int, title: str, body: str) -> None:
        requests.patch(
            f"{self.api_url}/pullrequests/{pr_number}?api-version=7.1-preview.1",
            headers=self._headers(),
            json={"title": title, "description": body}
        ).raise_for_status()

    def create_pr(self, from_branch: str, to_branch: str, title: str, body: str) -> str:
        res = requests.post(
            f"{self.api_url}/pullrequests?api-version=7.1-preview.1",
            headers=self._headers(),
            json={
                "sourceRefName": f"refs/heads/{from_branch}",
                "targetRefName": f"refs/heads/{to_branch}",
                "title": title,
                "description": body
            }
        )
        res.raise_for_status()
        return res.json()["url"]
