#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Library
import statistics

# Import other files
import data.database as db
from geopy.geocoders import Nominatim
from googletrans import Translator
from textblob import TextBlob


def checkAnalyze(city, state):
    # Variable
    valid_city = False
    valid_state = False
    capital_city = False

    # Change to small letter and then capitalize the first character
    modified_city = city.lower().capitalize()
    modified_state = state.lower().capitalize()

    # Query database
    result = db.getCity(modified_city, modified_state)

    if not result:
        return valid_city, valid_state, capital_city, city, state
    else:
        valid_city = True
        valid_state = True

    for i in result:
        if i['capital'] == 'admin':
            capital_city = True

    return valid_city, valid_state, capital_city, modified_city, modified_state


def getGeolocation(address):
    # Getting bounding box and address
    geolocator = Nominatim(user_agent="sentiment_analyze")
    location = geolocator.geocode(address)
    bounding_box = location.raw['boundingbox']

    return location, bounding_box


def removeEmoji(string):
    newString = string.encode('ascii', 'ignore').decode('ascii')
    return newString


def translateLanguage(data):
    # Variable
    text = []

    # Translate language
    translator = Translator()

    # Remove emoji before translating
    for i in data:
        text.append(removeEmoji(i))

    # Bulk translate
    translators = translator.translate(text, dest='en')

    return translators


def sentimentAnalysis(data):
    # Variable
    polarity_total = []
    pos = 0
    neg = 0

    for i in data:
        blob = TextBlob(i)
        polarity_total.append(blob.polarity)
        if blob.sentiment.polarity > 0:
            pos += 1
        else:
            neg += 1

    # Calculate the mean
    polarity_mean = statistics.mean(polarity_total)

    # Create dict to return the output
    output = {"positive": pos, "negative": neg, "polarity_mean": polarity_mean}

    return output


### This working is not done yet ###
def getAurin():
    # Variable
    aus_state = ['Victoria', 'New South Wales', 'Queensland', 'Western Australia', 'South Australia', 'Tasmania',
                 'Australian Capital Territory', 'Northern Territory']
    aurin_state = ['Rest of Vic.', 'Rest of NSW', 'Rest of Qld', 'Rest of WA', 'Rest of SA', 'Rest of Tas.',
                   'Australian Capital Territory', 'Rest of NT']
    aurin_city = ['Greater Melbourne', 'Greater Sydney', 'Greater Brisbane', 'Greater Perth', 'Greater Adelaide',
                  'Greater Hobart', 'Australian Capital Territory', 'Greater Darwin']
    data = []
    location = []

    # Get value from aurin
    aurin_data = db.getLifeExpectancy()

    # Extract the data
    for i in aurin_data:
        data.append({'location': i['feature_name'], 'life_expectancy': i['life_expectancy_p_2015_17']})
        location.append(i['feature_name'])

    return None
