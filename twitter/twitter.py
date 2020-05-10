# Library
import tweepy
from cloudant.client import CouchDB
import setting as cf

# Authentication
auth = tweepy.OAuthHandler(cf.consumer_key, cf.consumer_secret)
auth.set_access_token(cf.access_token, cf.access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

class TwitterStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        print(status.text)
        storeData(status._json)

    def on_error(self, status_code):
        if status_code == 420:
            return False

def storeData(data):
    client = CouchDB(cf.db_user, cf.db_password, url='http://{}:{}'.format(cf.db_host, cf.db_port), connect=True)
    db = client["twitter"]
    create_doc = db.create_document(data)

    # Check that the document exists in the database
    if create_doc.exists():
        print("New data successfully store")
    else:
        print("Failed creating the doucment")

if __name__ == '__main__':
    twitterStreamListener = TwitterStreamListener()
    twitterStream = tweepy.Stream(auth = api.auth, listener = TwitterStreamListener())

    # Australia bounding box
    twitterStream.filter(locations=[111.560497, -39.244618, 155.461864, -11.021575])