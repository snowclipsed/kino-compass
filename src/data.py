import json
import os



def load_tweets(tweet_path:str):
    with open(tweet_path) as f:
        return json.load(f)

def save_tweets(tweets, tweet_path:str):
    with open(tweet_path, 'w') as f:
        json.dump(tweets, f)

def extract_info(tweets):
    return [
        {
            "id": tweet["tweet"]["id"],
            "user_id": tweet["tweet"]["user"]["id"],
            "text": tweet["tweet"]["full_text"],
            "created_at": tweet["tweet"]["created_at"],
        } for tweet in tweets
    ]

tweet_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'tweets.json')
tweets = load_tweets(tweet_path)

