import os
import traceback
from queue import Queue
from threading import Thread

import tweepy
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from models.twitter import *
from utils.parse import Parser
from utils.prog_globals import db_tweet as db_raw, db_parsed, db_ref, logger

auth = tweepy.OAuthHandler(os.getenv("TWITTER_CONSUMER_KEY"), os.getenv("TWITTER_CONSUMER_SECRET_KEY"))
auth.set_access_token(os.getenv("TWITTER_ACCESS_TOKEN"), os.getenv("TWITTER_ACCESS_TOKEN_SECRET"))
api = tweepy.API(auth, wait_on_rate_limit=True, retry_count=3, retry_delay=60, timeout=1000)
tweet_router = APIRouter()
STARTED = False


class TwitterStreamListener(tweepy.StreamListener):
    def __init__(self, should_run: bool = True, workers=4):
        super().__init__()
        self.process_thread = None
        self.should_run = should_run
        self.message_queue = Queue()

        for i in range(workers):
            t = Thread(target=self.populate_db)
            t.daemon = True
            t.start()

    def on_status(self, status):
        print(status.text)
        self.message_queue.put(status._json)
        return self.should_run

    def on_error(self, status_code):
        if status_code == 420:
            return False

    def on_disconnect(self, notice):
        global STARTED
        logger.error("Stream Disconnected!", notice)
        STARTED = False
        args = TweetStreamRequest(action="start")
        handle_stream(args)

    def on_exception(self, exception):
        global STARTED
        logger.error("Stream Exception! Restarting stream", exception)
        STARTED = False
        args = TweetStreamRequest(action="start")
        handle_stream(args)

    def populate_db(self):
        while True:
            data = self.message_queue.get()
            raw_doc = db_raw.create_document(data)
            try:
                parser = Parser(data)
                parser.init_parse()
                params = parser.get_storable_params()
                params["reference_id"] = raw_doc["_id"]
                parsed_doc = db_parsed.create_document(params)
                # Check that the document exists in the database
                if raw_doc.exists() and parsed_doc.exists():
                    logger.info(f"RAW_REF: {raw_doc['_id']} :: PARSE_REF: {parsed_doc['_id']}")
                    db_ref.create_document(dict(text=data["text"], raw_ref=raw_doc['_id'], parse_ref=parsed_doc['_id']))
                else:
                    print("Failed creating tweet! Already exists!")
            except BaseException as e:
                logger.error(type(e), e)
                logger.error(traceback.format_exc())
                db_ref.create_document(dict(text=data["text"], raw_ref=raw_doc['_id'], parse_ref=None))
            self.message_queue.task_done()


twitterStreamListener = TwitterStreamListener()
twitterStream = tweepy.Stream(auth=api.auth, listener=twitterStreamListener)


@tweet_router.get("/")
def get_stream_info():
    return "Stream is running" if STARTED else "Stream is inactive"


@tweet_router.post("/",
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
def handle_stream(obj: TweetStreamRequest):
    global STARTED
    if obj.action == "start":
        if not STARTED or not twitterStream.running:
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
