import os

from globals import db_parsed, db_ref, db_oldTweet, db_tweet as db_raw
from parse import Parser

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

if __name__ == "__main__":
    for document in db_oldTweet:
        try:
            populate_db(document)
        except:
            pass