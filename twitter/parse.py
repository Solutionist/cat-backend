from functools import partial, wraps

from globals import db_aurin as db
from googletrans import Translator
from preprocessors import prep_for_sentiment, prep_for_translation
from shapely.geometry import Polygon, Point
from textblob import TextBlob

translator = Translator()

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
    @wraps(fn)
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
            self.text = self.translate(prep_for_translation(self.text)).text
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
                return dict(code=code, city=code_map.__getitem__(code)[0]["value"])
        return dict()
