#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Partial
from typing import List
from pydantic import BaseModel

class SentimentOutput(BaseModel):
    total_text: int
    positive: int
    negative: int
    polarity_mean: float

class SentimentAnalyze(BaseModel):
    city: str
    state: str
    language: str
    bounding_box: list
    output: SentimentOutput

response_error = {
    400: {"description": "Bad Request"},
    404: {"description": "Missing input variable"}
}