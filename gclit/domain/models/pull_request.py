# domain/models/pull_request.py
from pydantic import BaseModel

from gclit.domain.models.common import Lang


class PullRequestContext(BaseModel):
    diff: str
    branch_from: str
    branch_to: str
    lang: Lang = "en"


class PullRequestInfo(BaseModel):
    pr_number: int
    branch_from: str
    branch_to: str
