import logging
import os

import nltk
from cloudant.client import CouchDB, CouchDatabase
from dotenv import load_dotenv
from shapely.geometry import Polygon

try:
    from utils.database_setup import setup
except (ImportError, ModuleNotFoundError):
    from database_setup import setup

if os.getenv("HTTP_PROXY"):
    nltk.set_proxy(os.getenv("HTTP_PROXY"))
nltk.download("punkt")
load_dotenv()
root_dir = os.path.dirname(os.path.realpath(__file__)).rsplit(os.sep, 1)[0]

client = CouchDB(os.getenv("COUCH_USER"), os.getenv("COUCH_PASSWORD"),
                 url='http://{}:{}'.format(os.getenv("COUCH_URL"), os.getenv("COUCH_PORT")), connect=True,
                 auto_renew=True)

try:
    db_aurin: CouchDatabase = client[os.getenv("DB_AURIN")]
    db_ref: CouchDatabase = client[os.getenv("DB_REF")]
    db_tweet: CouchDatabase = client[os.getenv("DB_TWEET")]
    db_parsed: CouchDatabase = client[os.getenv("DB_PARSE")]
    # db_oldTweet = client[os.getenv("DB_OLD_TWEET")]
except BaseException as e:
    print(type(e), e)
    setup(client)
    db_aurin: CouchDatabase = client[os.getenv("DB_AURIN")]
    db_ref: CouchDatabase = client[os.getenv("DB_REF")]
    db_tweet: CouchDatabase = client[os.getenv("DB_TWEET")]
    db_parsed: CouchDatabase = client[os.getenv("DB_PARSE")]
    # db_oldTweet = client[os.getenv("DB_OLD_TWEET")]

code_map = dict()
polys = dict()
# From Views
try:
    code_map_view = db_aurin.get_view_result('_design/city_views', "code_map")
    code_coords_view = db_aurin.get_view_result('_design/city_views', "code_coords")

    for cm, cc in zip(code_map_view, code_coords_view):
        try:
            code_map.update({cm["key"]: cm["value"]})
            polys.update({cc["key"]: Polygon(
                [k for i in cc["value"] for j in i for k in j])})
        except KeyError:
            pass

except BaseException as e:
    for doc in db_aurin.__iter__(remote=True):
        try:
            code_map.update({doc["properties"]["feature_code"]: doc["properties"]["feature_name"]})
            polys.update({doc["properties"]["feature_code"]: Polygon(
                [k for i in doc["geometry"]["coordinates"] for j in i for k in j])})
        except KeyError:
            pass

logging.basicConfig(filename=os.getenv("LOG_FILENAME"), level=eval(os.getenv("LOG_LEVEL")),
                    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
                    datefmt="%d-%m-%Y %H:%M:%S")
logger = logging.getLogger("application_logger")
