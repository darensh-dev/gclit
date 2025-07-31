# domain/services/git_port.py
from abc import ABC, abstractmethod

from gclit.domain.models.pull_request import PullRequestInfo


class GitProvider(ABC):
    @abstractmethod
    def get_stash_diff(self) -> str:
        pass

    @abstractmethod
    def get_branch_name(self) -> str:
        pass

    @abstractmethod
    def get_branch_diff(self, from_branch: str, to_branch: str) -> str:
        pass

    @abstractmethod
    def get_pr_diff_by_number(self, pr_number: int) -> PullRequestInfo:
        pass

    @abstractmethod
    def update_pr(self, pr_number: int, title: str, body: str) -> None:
        pass

    @abstractmethod
    def create_pr(self, from_branch: str, to_branch: str, title: str, body: str) -> str:
        """Returns PR URL or ID"""
        pass

