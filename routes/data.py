from enum import Enum
from functools import partial

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from models.data import DataResponse, SINGLECANDIDATE_KEYS
from utils.prog_globals import db_parsed

data_router = APIRouter()


class GroupLevels(str, Enum):
    total = "1"
    emotion = "2"
    year = "3"


view_result = partial(db_parsed.get_view_result, ddoc_id='custom', view_name="code_senti_lang", raw_result=True,
                      reduce=True)


@data_router.get("/", response_model=DataResponse, response_model_exclude_unset=True)
def get_data(group_level: GroupLevels):
    # group_level-> 1: Place <> 2: 1, Emotion <> 3: 2, Year
    result = view_result(group_level=int(group_level.value))
    if result:
        result = filter(lambda x: None not in x["key"], result["rows"])
        result = [dict(zip(SINGLECANDIDATE_KEYS[:int(group_level.value)], r["key"]), count=r["value"]) for r in result]

    return JSONResponse(result, status_code=200 if result else 204)


@data_router.get("/{_id}", response_model=DataResponse, response_model_exclude_unset=True)
def get_data(_id: str, group_level: GroupLevels):
    # group_level-> 1: Place <> 2: 1, Emotion <> 3: 2, Year
    result = view_result(group_level=int(group_level.value))
    if result:
        result = filter(lambda x: _id == x["key"][0], result["rows"])
        result = [dict(zip(SINGLECANDIDATE_KEYS[:int(group_level.value)], r["key"]), count=r["value"]) for r in result]

    return JSONResponse(result, status_code=200 if result else 204)
