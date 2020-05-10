#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Python Library
import logging
import uvicorn
from fastapi import FastAPI, HTTPException, Header

# Others
import setting.config as config
import router.route as route

# logging
logging.basicConfig(filename=config.filename, level=eval(config.log_level), format="%(asctime)s [%(name)s] %(levelname)s: %(message)s", datefmt="%d-%m-%Y %H:%M:%S")

# App
app = FastAPI(title="Assignment 2 - Cloud & Cluster API", version="1.0", description="Assignment 2 API endpoints to connect to CouchDB", docs_url="/docs", redoc_url=None)

# Add route
app.include_router(route.router, tags=["Sentiment Analysis"])

if __name__ == "__main__":    
    # Uvicorn
    uvicorn.run(app, host=config.g_host, port=config.g_port, log_level="info")

    # Gunicorn logging
    # app.run()