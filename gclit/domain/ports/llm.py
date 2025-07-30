# domain/services/llm.py
from abc import ABC, abstractmethod
from gclit.domain.models.commit_message import CommitContext
from gclit.domain.models.pull_request import PullRequestContext 

class LLMProvider(ABC):
    @abstractmethod
    def generate_commit_message(self, context: CommitContext) -> str:
        pass

    @abstractmethod
    def generate_pr_documentation(self, context: PullRequestContext) -> dict:
        """Returns dict with 'title' and 'body' keys"""
        pass