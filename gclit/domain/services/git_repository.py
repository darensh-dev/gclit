# domain/services/git_repository.py
from abc import ABC, abstractmethod

class GitRepository(ABC):
    @abstractmethod
    def get_diff_between_branches(self, from_branch: str, to_branch: str) -> str:
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
