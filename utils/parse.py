# COMP90024 Project - Team 34
# Lokesh Sai Sri Harsha Sankarasetty, Melbourne, [1130612]
# Kanch Vatcharotayan, Melbourne, [1132855]
# Sai Deepthi Amancha, Melbourne, [1051388]
# Josin Saji Abraham, Melbourne, [1129428]
# Kush Garg, Melbourne, [1146696]

import os
from functools import wraps

from google.cloud import translate_v2 as translate
from shapely.geometry import Polygon, Point
from textblob import TextBlob

try:
    from utils.preprocessors import prep_for_sentiment, prep_for_translation
    from utils.prog_globals import code_map, polys, logger, root_dir
except (ImportError, ModuleNotFoundError):
    from preprocessors import prep_for_sentiment, prep_for_translation
    from prog_globals import code_map, polys, logger, root_dir

translator = translate.Client.from_service_account_json(os.path.join(
    root_dir, os.getenv("GOOGLE_APPLICATION_CREDENTIALS")))


def track_fn_call(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        wrapper.is_called = True
        return fn(*args, **kwargs)

    wrapper.is_called = False
    return wrapper


def translate_text(text, src, dst="en"):
    if not text:
        return text, src
    response = dict(translator.translate(text, target_language=dst))
    return response["translatedText"], response["detectedSourceLanguage"]


class Parser:
    def __init__(self, tweet: dict):
        self.tweet = tweet
        if hasattr(self.tweet, "extended_tweet"):
            self.text = self.tweet["extended_tweet"]["full_text"]
        else:
            self.text = tweet.get("text")

        if tweet["geo"] is None:
            if tweet["place"]["place_type"] == "poi":
                self.location = Point(tweet["place"]["bounding_box"]["coordinates"][0][0])
            else:
                self.location = Polygon(tweet["place"]["bounding_box"]["coordinates"][0])
        else:
            self.location = Point(tweet["coordinates"]["coordinates"])
        self.inferred_language = tweet.get("lang")
        self.__transition_text = None
        self.inferred_text = self.inferred_location = self.inferred_sentiment = self.inferred_year = None

    def get_storable_params(self):
        params = filter(lambda kv: "inferred" in kv[0], self.__dict__.items())
        if not getattr(self.init_parse, "is_called"):
            raise AttributeError("call `init_parse` before requesting for inferred params")
        return {kv[0]: kv[1] for kv in params}

    @track_fn_call
    def init_parse(self):
        # Translate if from different language
        if self.inferred_language != "en":
            logger.info(f"Input language: {self.inferred_language}")
            self.text, self.inferred_language = translate_text(prep_for_translation(self.text), self.inferred_language)
        self.text = prep_for_sentiment(self.text)
        self.__transition_text = TextBlob(self.text)
        self.inferred_text = self.__transition_text.stripped
        polarity = self.__transition_text.polarity
        self.inferred_sentiment = dict(
            emotion="Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral",
            polarity=abs(polarity)
        )
        self.inferred_location = self.__get_location()
        self.inferred_year = self.tweet["created_at"].split(" ")[-1]

    def __get_location(self):
        bbox = self.location
        for code, polygon in polys.items():
            if polygon.intersects(bbox) or polygon.contains(bbox):
                return dict(code=code, city=code_map[code])
        return dict()
