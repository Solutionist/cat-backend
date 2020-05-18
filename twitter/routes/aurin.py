from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from utils.prog_globals import db_aurin, polys

aurin_router = APIRouter()


def get_query_results(selector):
    docs = db_aurin.get_query_result(selector)
    response_params = list()
    for doc in docs:
        props = doc["properties"]
        centroid = polys[props["feature_code"]].centroid
        response_params.append(
            dict(
                code=props["feature_code"],
                name=props["feature_name"],
                pin=(centroid.x, centroid.y),
                life_expectancy=props["life_expectancy_p_2015_17"]
            )
        )
    return response_params


@aurin_router.get("/")
def get_aurin_data():
    selector = {
        '_id': {
            "$gt": None
        }
    }
    result = get_query_results(selector)
    return JSONResponse(result, status_code=200 if result else 204)


@aurin_router.get("/{_id}")
def get_aurin_data(_id: Optional[str]):
    selector = {
        "$or": [
            {
                'properties.feature_code': {
                    "$eq": _id
                }
            },
            {
                'properties.feature_name': {
                    "$eq": _id
                }
            }
        ]
    }
    # selector = {
    #     'properties.feature_code': {
    #         "$eq": _id
    #     }
    # }
    result = get_query_results(selector)
    return JSONResponse(result, status_code=200 if result else 204)
