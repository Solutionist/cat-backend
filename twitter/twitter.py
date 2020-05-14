import os

import tweepy
import uvicorn
from cloudant.client import CouchDB
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter
from parse import Parser
from pydantic import BaseModel

app = FastAPI()
router = APIRouter()

load_dotenv()

client = CouchDB(os.getenv("COUCH_USER"), os.getenv("COUCH_PASSWORD"),
                 url='http://{}:{}'.format(os.getenv("COUCH_URL"), os.getenv("COUCH_PORT")), connect=True)
db_raw = client["twitter"]
db_parsed = client["parsed_data"]
db_ref = client["reference"]

auth = tweepy.OAuthHandler(os.getenv("TWITTER_CONSUMER_KEY"), os.getenv("TWITTER_CONSUMER_SECRET_KEY"))
auth.set_access_token(os.getenv("TWITTER_ACCESS_TOKEN"), os.getenv("TWITTER_ACCESS_TOKEN_SECRET"))
api = tweepy.API(auth, wait_on_rate_limit=True)

STARTED = False


class TwitterStreamListener(tweepy.StreamListener):
    def __init__(self, should_run: bool = True):
        super().__init__()
        self.should_run = should_run

    def on_status(self, status):
        print(status.text, end="\t")
        populate_db(status._json)
        return self.should_run

    def on_error(self, status_code):
        if status_code == 420:
            return False


def populate_db(data):
    raw_doc = db_raw.create_document(data)
    try:
        parser = Parser(data)
        parser.init_parse()
        params = parser.get_storable_params()
        params["reference_id"] = raw_doc["_id"]
        parsed_doc = db_parsed.create_document(params)
        # Check that the document exists in the database
        if raw_doc.exists() and parsed_doc.exists():
            print(f"RAW_REF: {raw_doc['_id']} :: PARSE_REF: {parsed_doc['_id']}")
            db_ref.create_document(dict(text=data["text"], raw_ref=raw_doc['_id'], parse_ref=parsed_doc['_id']))
        else:
            print("Failed creating tweet! Already exists!")
    except BaseException as e:
        print(type(e), e)
        db_ref.create_document(dict(text=data["text"], raw_ref=raw_doc['_id'], parse_ref=None))


twitterStreamListener = TwitterStreamListener()
twitterStream = tweepy.Stream(auth=api.auth, listener=twitterStreamListener)


class Key(BaseModel):
    action: str


@router.post("/tweet_stream")
async def handle_stream(obj: Key):
    global STARTED
    if obj.action == "start":
        if not STARTED:
            print("<< Started tweet stream >>")
            twitterStreamListener.should_run = True
            twitterStream.filter(locations=[111.560497, -39.244618, 155.461864, -11.021575], is_async=True)
            STARTED = True
            return "STARTED"
        else:
            return "ALREADY RUNNING"
    elif obj.action in ["pause", "stop"]:
        if STARTED:
            print("<< Ended tweet stream >>")
            twitterStreamListener.should_run = False
            STARTED = False
            return "STOPPED"
        else:
            return "NOT RUNNING"
    else:
        return "NOT A VALID KEY", 400


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
