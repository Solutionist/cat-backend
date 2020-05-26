import json
import os

from cloudant.client import CouchDB
from cloudant.design_document import DesignDocument

root_dir = os.path.dirname(os.path.realpath(__file__)).rsplit(os.sep, 1)[0]


def setup(_client):
    db_name = os.getenv("DB_REF")
    try:
        db = _client[db_name]
    except KeyError:
        print(f"<< database: `{db_name}` does not exist. Creating a new database. >>")
        db = _client.create_database(db_name, False)

    db_name = os.getenv("DB_AURIN")
    try:
        db = _client[db_name]
    except KeyError:
        print(f"<< database: `{db_name}` does not exist. Creating a new database. >>")
        db = _client.create_database(db_name, False)

    aurin_data = json.load(open(os.path.join(root_dir, "aurin.json"), "r"))
    if db.doc_count() < 15:
        print(f"<-- Inserting into `{db_name}` db -->")
        for feature in aurin_data.get("features"):
            db.create_document(feature)
        print("<---- Insertion complete ----->")
    else:
        print(f"<---- `{db_name}` already populated ----->")
        del aurin_data

    master_view = "_design/city_views"
    if master_view not in db.list_design_documents():
        print(f"<--- Creating views for `{db_name}` --->")
        all_city_views = DesignDocument(db, document_id=master_view, partitioned=False)
        all_city_views.add_view("code_map",
                                "function (doc) {\n  emit(doc.properties.gcc_code16, doc.properties.gccsa_name);\n}")
        all_city_views.add_view("code_coords",
                                "function (doc) {\n  emit(doc.properties.gcc_code16, doc.geometry.coordinates);\n}")
        all_city_views.save()
        print("<-- Creation complete -->")
    else:
        print(f"<--- Required views for `{db_name}` are already created --->")

    db_name = os.getenv("DB_PARSE")
    try:
        db = _client[db_name]
    except KeyError:
        print(f"database: `{db_name}` does not exist. Creating a new database.")
        db = _client.create_database(db_name, False)

    master_view = "_design/custom"
    if master_view not in db.list_design_documents():
        print(f"<--- Creating views for `{db_name}` --->")
        all_custom_views = DesignDocument(db, document_id=master_view, partitioned=False)
        all_custom_views.add_view("code_senti_year",
                                  map_func="""
                                        function (doc) {
                                            emit([doc.inferred_location.code, 
                                                doc.inferred_sentiment.emotion,
                                                doc.inferred_year], 
                                            1);
                                        }
                                      """,
                                  reduce_func="_sum")
        all_custom_views.add_view("code_senti_lang",
                                  map_func="""
                                                function (doc) {
                                                    emit([doc.inferred_location.code, 
                                                        doc.inferred_sentiment.emotion,
                                                        doc.inferred_language], 
                                                    1);
                                                }
                                              """,
                                  reduce_func="_sum")
        all_custom_views.save()
        print("<-- Creation complete -->")
    else:
        print(f"<--- Required views for `{db_name}` are already created --->")

    db_name = os.getenv("DB_TWEET")
    try:
        db = _client[db_name]
    except KeyError:
        print(f"database: `{db_name}` does not exist. Creating a new database.")
        db = _client.create_database(db_name, False)


if __name__ == '__main__':
    client = CouchDB(os.getenv("COUCH_USER"), os.getenv("COUCH_PASSWORD"),
                     url='http://{}:{}'.format(os.getenv("COUCH_URL"), os.getenv("COUCH_PORT")), connect=True)

    setup(client)
