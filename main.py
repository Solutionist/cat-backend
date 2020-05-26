# COMP90024 Project - Team 34
# Lokesh Sai Sri Harsha Sankarasetty, Melbourne, [1130612]
# Kanch Vatcharotayan, Melbourne, [1132855]
# Sai Deepthi Amancha, Melbourne, [1051388]
# Josin Saji Abraham, Melbourne, [1129428]
# Kush Garg, Melbourne, [1146696]

import os

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from routes import *
from utils.language_code import LANGUAGE_CODES

app = FastAPI(title="Cloud & Cluster API", version="1.0",
              description="Assignment 2 API endpoints", docs_url="/docs", redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Add route
app.include_router(tweet_router, prefix="/tweet_stream", tags=["Twitter Stream Handler"])
app.include_router(aurin_router, prefix="/aurin", tags=["Aurin data API"])
app.include_router(data_router, prefix="/data", tags=["Twitter analysis data API"])


@app.get("/language_codes", tags=["Language code data API"])
def get_lang_codes():
    return LANGUAGE_CODES


@app.get("/language_codes/{language}", tags=["Language code data API"])
def get_lang_codes(language: str):
    return LANGUAGE_CODES.get(language, "")


if __name__ == "__main__":
    host = os.getenv("SERVER_HOST")
    port = int(os.getenv("SERVER_PORT"))
    uvicorn.run(app, host=host, port=port)
