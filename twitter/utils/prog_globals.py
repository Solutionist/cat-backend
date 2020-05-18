import logging
import os

import nltk
from cloudant.client import CouchDB
from cloudant.result import Result
from dotenv import load_dotenv
from shapely.geometry import Polygon

from utils.database_setup import setup

nltk.download("punkt")
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
