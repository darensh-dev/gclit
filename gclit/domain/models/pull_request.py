# domain/models/pull_request.py
from pydantic import BaseModel

from gclit.domain.models.common import Lang


class PullRequestContext(BaseModel):
    diff: str
    from_branch: str
    to_branch: str
    lang: Lang = "en"


class PullRequestInfo(BaseModel):
    pr_number: int
    from_branch: str
    to_branch: str
