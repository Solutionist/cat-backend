from typing import List

from pydantic import BaseModel


class SingleCandidate(BaseModel):
    code: str
    emotion: str
    year: int
    language: str
    count: int
    count_log: float


SINGLECANDIDATE_KEYS = list(SingleCandidate.__fields__.keys())


class DataResponse(BaseModel):
    all: List[SingleCandidate]
