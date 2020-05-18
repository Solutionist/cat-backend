import os

import uvicorn
from fastapi import FastAPI

from routes import *

app = FastAPI(title="Cloud & Cluster API", version="1.0",
              description="Assignment 2 API endpoints", docs_url="/docs", redoc_url=None)

# Add route
app.include_router(tweet_router, prefix="/tweet_stream", tags=["Twitter Stream Handler"])
app.include_router(aurin_router, prefix="/aurin", tags=["Aurin data API"])
app.include_router(data_router, prefix="/data", tags=["Twitter analysis data API"])

if __name__ == "__main__":
    host = os.getenv("SERVER_HOST")
    port = int(os.getenv("SERVER_PORT"))
    uvicorn.run(app, host=host, port=port)
