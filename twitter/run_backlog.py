import os

from cloudant.client import CouchDB
from dotenv import load_dotenv
from parse import Parser

load_dotenv()

client = CouchDB(os.getenv("COUCH_USER"), os.getenv("COUCH_PASSWORD"),
                 url='http://{}:{}'.format(os.getenv("COUCH_URL"), os.getenv("COUCH_PORT")), connect=True)
db_raw = client["twitter"]
db_parsed = client["parsed_data"]
db_ref = client["reference"]

for raw_doc in db_raw:
    try:
        parser = Parser(raw_doc)
        parser.init_parse()
        params = parser.get_storable_params()
        params["reference_id"] = raw_doc["_id"]
        parsed_doc = db_parsed.create_document(params)
        # Check that the document exists in the database
        if raw_doc.exists() and parsed_doc.exists():
            print(f"{raw_doc['text']} RAW_REF: {raw_doc['_id']} :: PARSE_REF: {parsed_doc['_id']}")
            db_ref.create_document(dict(text=raw_doc["text"], raw_ref=raw_doc['_id'], parse_ref=parsed_doc['_id']))
        else:
            print("Failed creating tweet! Already exists!")
    except BaseException as e:
        print(type(e), e)
        db_ref.create_document(dict(text=raw_doc["text"], raw_ref=raw_doc['_id'], parse_ref=None))
