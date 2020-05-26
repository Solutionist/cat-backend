# COMP90024 Project - Team 34
# Lokesh Sai Sri Harsha Sankarasetty, Melbourne, [1130612]
# Kanch Vatcharotayan, Melbourne, [1132855]
# Sai Deepthi Amancha, Melbourne, [1051388]
# Josin Saji Abraham, Melbourne, [1129428]
# Kush Garg, Melbourne, [1146696]

import math
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


view_result_lang = partial(db_parsed.get_view_result, ddoc_id='custom', view_name="code_senti_lang", raw_result=True,
                           reduce=True)
view_result_year = partial(db_parsed.get_view_result, ddoc_id='custom', view_name="code_senti_year", raw_result=True,
                           reduce=True)


@data_router.get("/", response_model=DataResponse, response_model_exclude_unset=True)
def get_data(group_level: GroupLevels, group_by: str = "year"):
    # group_level-> 1: Place <> 2: 1, Emotion <> 3: 2, Year
    keys = list(SINGLECANDIDATE_KEYS)
    if group_by in ["yr", "year"]:
        result = view_result_year(group_level=int(group_level.value))
    elif group_by in ["lang", "language"]:
        result = view_result_lang(group_level=int(group_level.value))
        keys.remove("year")
    else:
        return JSONResponse({"msg": "Not a valid grouping. Try lang|language : year|yr"}, status_code=400)
    if result:
        result = filter(lambda x: None not in x["key"], result["rows"])
        result = [dict(zip(keys[:int(group_level.value)], r["key"]), count=r["value"],
                       count_log=0 if r["value"] < 1 else math.log(r["value"])) for r in result]

    return JSONResponse(result, status_code=200 if result else 204)


@data_router.get("/{_id}", response_model=DataResponse, response_model_exclude_unset=True)
def get_data(_id: str, group_level: GroupLevels, group_by: str = "year"):
    # group_level-> 1: Place <> 2: 1, Emotion <> 3: 2, Year
    keys = list(SINGLECANDIDATE_KEYS)
    if group_by in ["yr", "year"]:
        result = view_result_year(group_level=int(group_level.value))
    elif group_by in ["lang", "language"]:
        result = view_result_lang(group_level=int(group_level.value))
        keys.remove("year")
    else:
        return JSONResponse({"msg": "Not a valid grouping. Try lang|language : year|yr"}, status_code=400)
    if result:
        result = filter(lambda x: _id == x["key"][0], result["rows"])
        result = [dict(zip(keys[:int(group_level.value)], r["key"]), count=r["value"],
                       count_log=0 if r["value"] < 1 else math.log(r["value"]))
                  for r in result]

    return JSONResponse(result, status_code=200 if result else 204)
