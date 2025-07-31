# domain/services/git_port.py
from abc import ABC, abstractmethod


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
    def get_pr_diff_by_number(self, pr_number: int) -> str:
        pass

    @abstractmethod
    def update_pr(self, pr_number: int, title: str, body: str) -> None:
        pass

    @abstractmethod
    def create_pr(self, from_branch: str, to_branch: str, title: str, body: str) -> str:
        """Returns PR URL or ID"""
        pass


# pr --from develop --to main