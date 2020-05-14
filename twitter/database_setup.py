import json
import os

from cloudant.client import CouchDB
from cloudant.design_document import DesignDocument
from dotenv import load_dotenv

print(f"Environment file loaded: {load_dotenv()}")


def str_add(s1: str, s2: str, delimiter: str = "") -> str:
    return (s1 if s1 else "") + delimiter + (s2 if s2 else "")


def flat_map(dict_o: dict) -> dict:
    returnable = dict()
    for k, v in dict_o.items():
        if isinstance(v, dict):
            v = flat_map(v)
            returnable.update({str_add(k, _k, "_"): str(_v) for _k, _v in v.items()})
        else:
            returnable.update({k: str(v)})
    return returnable


if __name__ == '__main__':
    client = CouchDB(os.getenv("COUCH_USER"), os.getenv("COUCH_PASSWORD"),
                     url='http://{}:{}'.format(os.getenv("COUCH_URL"), os.getenv("COUCH_PORT")), connect=True)
    try:
        db = client["reference"]
    except KeyError:
        print("<< database: `reference` does not exist. Creating a new database. >>")
        db = client.create_database("reference", False)

    try:
        db = client["aurin"]
    except KeyError:
        print("<< database: `aurin` does not exist. Creating a new database. >>")
        db = client.create_database("aurin", False)

    aurin_data = json.load(open("aurin.json", "r"))
    if db.doc_count() < 15:
        print("<-- Inserting into aurin db -->")
        for feature in aurin_data.get("features"):
            feature["hash"] = hash(frozenset(flat_map(feature).items()))
            db.create_document(feature)
        print("<---- Insertion complete ----->")
    else:
        print("<---- `aurin` already populated ----->")
        del aurin_data

    master_view = "_design/city_views"
    if master_view not in db.list_design_documents():
        print("<--- Creating views for `aurin` --->")
        all_city_views = DesignDocument(db, document_id=master_view, partitioned=False)
        all_city_views.add_view("code_map",
                                "function (doc) {\n  emit(doc.properties.gcc_code16, doc.properties.gccsa_name);\n}")
        all_city_views.add_view("code_coords",
                                "function (doc) {\n  emit(doc.properties.gcc_code16, doc.geometry.coordinates);\n}")
        all_city_views.add_view("hash",
                                "function (doc) {\n  emit(doc.hash, 1);\n}")
        all_city_views.save()
        print("<-- Creation complete -->")
    else:
        print("<--- Required views for `aurin` are already created --->")

    try:
        db = client["parsed_data"]
    except KeyError:
        print("database: `parsed_data` does not exist. Creating a new database.")
        db = client.create_database("parsed_data", False)

    master_view = "_design/custom"
    if master_view not in db.list_design_documents():
        print("<--- Creating views for `parsed_data` --->")
        all_custom_views = DesignDocument(db, document_id=master_view, partitioned=False)
        all_custom_views.add_view("code_senti_lang",
                                  map_func="""
                                    function (doc) {
                                        emit([doc.inferred_location.city, 
                                            doc.inferred_sentiment.emotion, 
                                            doc.inferred_language,
                                            doc.inferred_year], 
                                        1);
                                    }
                                  """,
                                  reduce_func="_count")
        all_custom_views.save()
        print("<-- Creation complete -->")
    else:
        print("<--- Required views for `aurin` are already created --->")
