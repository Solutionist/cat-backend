from typing import List

from pydantic import BaseModel


class SingleCandidate(BaseModel):
    code: str
    emotion: str
    year: int
    count: int


SINGLECANDIDATE_KEYS = list(SingleCandidate.__fields__.keys())


class DataResponse(BaseModel):
    all: List[SingleCandidate]
