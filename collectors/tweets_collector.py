import os
import tweepy
from models.tweets import Tweets
from db.postgresql_connector import PostgreSQLConnector


def get_tweepy_api(consumer_key, consumer_secret_key, access_token, access_token_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    return api


def collect_tweets_data(tweepy_api):
    screen_name = 'nycoutages'
    pages = [status for status in
             tweepy.Cursor(tweepy_api.user_timeline, id=screen_name, count=200, include_rts=False).pages(16)]
    return pages


def store_tweets_to_postgres(tweets, postgres_session):
    for page in pages:
        for tweet in page:
            # if the tweet id is not already there
            if not postgres_session.query(Tweets).filter(Tweets.id == tweet.id).first():
                new_tweet = Tweets(id=tweet.id,
                                   created_at=tweet.created_at,
                                   tweet_text=tweet.text)
                db_session.add(new_tweet)
    db_session.commit()


if __name__ == '__main__':

    engine_string = os.environ.get('PG_ENGINE_STRING')
    if not engine_string:
        print('Please set variable PG_ENGINE_STRING to valid PostgreSQL connection')
        exit(8)

    consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
    consumer_secret_key = os.environ.get('TWITTER_CONSUMER_SECRET_KEY')
    access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

    if not consumer_key or not consumer_secret_key or not access_token or not access_token_secret:
        print('Please set variables for twitter access keys')
        exit(8)

    db_session = PostgreSQLConnector().connect(engine_string=engine_string)
    tweepy_api = get_tweepy_api(consumer_key, consumer_secret_key, access_token, access_token_secret)
    pages = collect_tweets_data(tweepy_api)
    store_tweets_to_postgres(pages, db_session)
