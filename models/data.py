# COMP90024 Project - Team 34
# Lokesh Sai Sri Harsha Sankarasetty, Melbourne, [1130612]
# Kanch Vatcharotayan, Melbourne, [1132855]
# Sai Deepthi Amancha, Melbourne, [1051388]
# Josin Saji Abraham, Melbourne, [1129428]
# Kush Garg, Melbourne, [1146696]

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
