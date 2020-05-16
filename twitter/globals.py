import os

from cloudant.client import CouchDB
from dotenv import load_dotenv

from database_setup import setup

load_dotenv()

client = CouchDB(os.getenv("COUCH_USER"), os.getenv("COUCH_PASSWORD"),
                 url='http://{}:{}'.format(os.getenv("COUCH_URL"), os.getenv("COUCH_PORT")), connect=True)

try:
    db_aurin = client[os.getenv("DB_AURIN")]
    db_ref = client[os.getenv("DB_REF")]
    db_tweet = client[os.getenv("DB_TWEET")]
    db_parsed = client[os.getenv("DB_PARSE")]
except BaseException as e:
    print(type(e), e)
    setup(client)
    db_aurin = client[os.getenv("DB_AURIN")]
    db_ref = client[os.getenv("DB_REF")]
    db_tweet = client[os.getenv("DB_TWEET")]
    db_parsed = client[os.getenv("DB_PARSE")]
