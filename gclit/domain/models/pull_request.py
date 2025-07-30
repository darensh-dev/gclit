# domain/models/pull_request.py
from pydantic import BaseModel


class PullRequestContext(BaseModel):
    diff: str
    branch_from: str
    branch_to: str
    lang: str = "en"


class PullRequestInfo(BaseModel):
    pr_number: int
    branch_from: str
    branch_to: str
