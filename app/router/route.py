#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Partial
# Import other files
import data.database as db
import router.language_code as lc
import router.logic as lg
import router.model as model
from fastapi import APIRouter, Form
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

# Create router
router = APIRouter()


# Endpoint
@router.post("/analyze", summary="Generate subtitles in other languages", response_model=model.SentimentAnalyze,
             responses={**model.response_error}, tags=["Sentiment Analysis"])
def sentiment_analyze(*, city: str = Form(..., description="the city/town name"),
                      state: str = Form(..., description="the state name"),
                      language: str = Form("en", description="the specific language to do the sentiment analyze")):
    # Variable
    text_input = []
    full_language = ""

    # Check if the input data is valid
    if city and state:
        valid_city, valid_state, capital_city, city, state = lg.checkAnalyze(city, state)

        # Return value if city or state does not exist
        if not valid_city or not valid_state:
            response = {
                'description': 'This city and/or state does not exist please try again'
            }
            payload = jsonable_encoder(response)
            return JSONResponse(content=payload)

        # Check language
        if language != "en":
            if language not in lc.LANGUAGE_CODES:
                response = {
                    'description': 'This languages does not exist please try again'
                }
                payload = jsonable_encoder(response)
                return JSONResponse(content=payload)

        # Change to full language name
        for key, value in lc.LANGUAGE_CODES.items():
            if language == key:
                full_language = value

        # Get bounding box for the address
        address = city + ', ' + state
        location, bounding_box = lg.getGeolocation(address)

        # Get data from twitter
        twitter = db.getText(address, 'place', language)

        if twitter == "Error: Does not find the value requested":
            response = {
                'description': 'No data from this city and/or state please try other state & city'
            }
            payload = jsonable_encoder(response)
            return JSONResponse(content=payload)

        # Extract text and put into list
        for i in twitter:
            text_input.append(i["text"])

        # Translate to english if the language is other language
        if language != "en":
            # Bulk translate
            translate_input = lg.translateLanguage(text_input)
            text_input = []
            for i in translate_input:
                text_input.append(i.text)

        # Do sentiment analyzes
        output = lg.sentimentAnalysis(text_input)

        response = {
            'city': city,
            'state': state,
            'language': full_language,
            'bounding_box': bounding_box,
            'output': {
                'total_text': len(text_input),
                'positive': output['positive'],
                'negative': output['negative'],
                'polarity_mean': output['polarity_mean']
            }
        }
        payload = jsonable_encoder(response)
        return JSONResponse(content=payload)

    # Missing required input value
    else:
        return JSONResponse(status_code=404, content={"description": "Missing input variable"})
