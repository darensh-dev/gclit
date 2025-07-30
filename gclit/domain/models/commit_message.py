# domain/models/commit_message.py
from pydantic import BaseModel

class CommitContext(BaseModel):
    diff: str
    branch_name: str
    lang: str = "en"
