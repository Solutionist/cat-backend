import os

import tweepy
import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from globals import db_tweet as db_raw, db_parsed, db_ref
from parse import Parser
from pydantic import BaseModel

app = FastAPI()
router = APIRouter()

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


class TweetStreamRequest(BaseModel):
    action: str


class TweetStreamResponse(BaseModel):
    message: str


@router.post("/tweet_stream",
             response_model=TweetStreamResponse,
             responses={
                 400: {"model": TweetStreamResponse, "description": "Validity of action"},
                 406: {"model": TweetStreamResponse, "description": "Cannot perform said action"},
                 200: {
                     "description": "Stream action to perform",
                     "content": {
                         "application/json": {
                             "example": {"action": "start|stop|pause"}
                         }
                     },
                 },
             }, )
async def handle_stream(obj: TweetStreamRequest):
    global STARTED
    if obj.action == "start":
        if not STARTED:
            twitterStreamListener.should_run = True
            twitterStream.filter(locations=[111.560497, -39.244618, 155.461864, -11.021575], is_async=True)
            STARTED = True
            print("<< Started tweet stream >>")
            return dict(message="Stream has been started")
        else:
            return JSONResponse(status_code=406,
                                content=dict(message="Stream is already running. Cannot start a new stream"))
    elif obj.action in ["pause", "stop"]:
        if STARTED:
            twitterStreamListener.should_run = False
            STARTED = False
            print("<< Ended tweet stream >>")
            return dict(message="Stream has been stopped")

        else:
            return JSONResponse(status_code=406, content=dict(
                message="Stream not started/inactive. Start stream before requesting to stop or pause"))
    else:
        return JSONResponse(status_code=400, content={"message": "Not a known action. Try start|pause|stop"})


app.include_router(router)

if __name__ == "__main__":
    host = os.getenv("SERVER_HOST")
    port = int(os.getenv("SERVER_PORT"))
    uvicorn.run(app, host=host, port=port)
