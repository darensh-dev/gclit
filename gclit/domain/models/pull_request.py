# domain/models/pull_request.py
from typing import Optional
from pydantic import BaseModel

from gclit.domain.models.common import Lang


class PullRequestContext(BaseModel):
    diff: str
    from_branch: str
    to_branch: str
    lang: Lang = "en"
    commit_history: Optional[str] = None

class PullRequestInfo(BaseModel):
    pr_number: int
    from_branch: str
    to_branch: str
