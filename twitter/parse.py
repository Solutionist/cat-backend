import datetime
import functools
import os
import re
from functools import partial

from cloudant.client import CouchDB
from dotenv import load_dotenv
from googletrans import Translator
from preprocessors import prep_for_sentiment, prep_for_translation
from shapely.geometry import Polygon, Point
from textblob import TextBlob

load_dotenv()
translator = Translator()
client = CouchDB(os.getenv("COUCH_USER"), os.getenv("COUCH_PASSWORD"),
                 url='http://{}:{}'.format(os.getenv("COUCH_URL"), os.getenv("COUCH_PORT")), connect=True)
db = client["aurin"]
code_map = db.get_view_result('_design/city_views', "code_map")
code_coords = db.get_view_result('_design/city_views', "code_coords")

polys = dict()
for doc in code_coords.all():
    try:
        polys.update({doc["key"]: Polygon(
            [k for i in doc["value"] for j in i for k in j])})
    except KeyError:
        pass


def track_fn_call(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        wrapper.is_called = True
        return fn(*args, **kwargs)

    wrapper.is_called = False
    return wrapper


class Parser:
    translate = partial(translator.translate, dest="en")

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
        self.__translated = None
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
        self.text = prep_for_translation(self.text)
        if self.inferred_language == "en":
            self.__transition_text = TextBlob(self.text)
        else:
            self.__translated = self.translate(self.text)
            self.text = prep_for_sentiment(self.__translated.text)
            self.__transition_text = TextBlob(self.text)
        self.inferred_text = self.__transition_text.stripped
        polarity = self.__transition_text.polarity
        self.inferred_sentiment = dict(
            emotion="Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral",
            polarity=abs(polarity)
        )
        self.inferred_location = self.__get_location()
        self.inferred_year = datetime.datetime.fromtimestamp(int(self.tweet["timestamp_ms"][:10])).year

    def __get_location(self):
        bbox = self.location
        for code, polygon in polys.items():
            if polygon.intersects(bbox) or polygon.contains(bbox):
                return dict(code=code, city=code_map.__getitem__(code)[0]["value"])
        return dict()

    @staticmethod
    def __remove_pattern(input_txt, pattern):
        r = re.findall(pattern, input_txt)
        for i in r:
            input_txt = re.sub(i, '', input_txt)
        return input_txt
