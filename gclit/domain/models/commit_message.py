# domain/models/commit_message.py
from typing import Optional
from pydantic import BaseModel
from gclit.domain.models.common import Lang


class CommitContext(BaseModel):
    diff: str
    branch_name: str
    lang: Lang = "en"
    commit_history: Optional[str] = None
