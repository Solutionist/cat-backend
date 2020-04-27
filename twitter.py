# Library
import tweepy
import pycouchdb
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
    server = pycouchdb.Server("http://{}:{}@localhost:{}/".format(cf.db_user, cf.db_password, cf.db_port))
    db = server.database("twitter")
    db.save(data)
    print("New data successfully store")

if __name__ == '__main__':
    twitterStreamListener = TwitterStreamListener()
    twitterStream = tweepy.Stream(auth = api.auth, listener = TwitterStreamListener())

    # First 4 is Melbourne then Sydney
    twitterStream.filter(locations=[144.704420,-38.020120,145.246870,-37.613297,151.056519,-34.002581,151.329803,-33.796268])