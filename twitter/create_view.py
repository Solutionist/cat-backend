# Library
from cloudant.design_document import DesignDocument
from cloudant.client import CouchDB

# File
import setting as cf

if __name__ == "__main__":
    client = CouchDB(cf.db_user, cf.db_password, url='http://{}:{}'.format(cf.db_host, cf.db_port), connect=True)
    db = client['twitter']

    language = ["en", "ar", "zh", "es", "hi", "th", "ja"]

    for i in language:
        text = DesignDocument(db, document_id='text_{}'.format(i), partitioned=False)
        text.add_view("place", "function(doc) {{ if (doc.lang == '{}') {{} emit(doc.place.full_name, [doc.text, doc.extended_tweet.full_text]); }} }}".format(i))
        text.add_view("date", "function(doc) {{ if (doc.lang == '{}') {{ emit(doc.created_at.slice(-4), [doc.place.full_name, doc.text, doc.extended_tweet.full_text]); }} }}".format(i))
        text.save()

    # For all languages
    text_all = DesignDocument(db, document_id='text_all', partitioned=False)
    text_all.add_view("place", "function(doc) { emit(doc.place.full_name, [doc.text, doc.extended_tweet.full_text]); }")
    text_all.add_view("date", "function(doc) { emit(doc.created_at.slice(-4), [doc.place.full_name, doc.text, doc.extended_tweet.full_text]); }")
    text_all.save()

