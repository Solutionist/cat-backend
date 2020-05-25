try:
    from utils.parse import Parser
    from utils.prog_globals import db_parsed, db_ref, db_tweet as db_raw
except (ImportError, ModuleNotFoundError):
    from parse import Parser
    from prog_globals import db_parsed, db_ref, db_tweet as db_raw
import traceback

with db_raw.custom_result(skip=0, include_docs=True, page_size=100) as result:
    for raw_doc in result:
        raw_doc = raw_doc["doc"]
        try:
            parser = Parser(raw_doc)
            parser.init_parse()
            params = parser.get_storable_params()
            params["reference_id"] = raw_doc["_id"]
            parsed_doc = db_parsed.create_document(params)
            # Check that the document exists in the database
            print(f"{raw_doc['text']} RAW_REF: {raw_doc['_id']} :: PARSE_REF: {parsed_doc['_id']}")
            db_ref.create_document(dict(text=raw_doc["text"], raw_ref=raw_doc['_id'], parse_ref=parsed_doc['_id']))
        except:
            try:
                print(traceback.print_exc())
                db_ref.create_document(dict(text=raw_doc["text"], raw_ref=raw_doc['_id'], parse_ref=None))
            except:
                print(traceback.print_exc())
