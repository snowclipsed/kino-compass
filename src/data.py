import json
from datetime import datetime, timedelta, timezone


from llama_cpp.llama_grammar import parse


def load_tweets(tweet_path:str):
    with open(tweet_path) as f:
        return json.load(f)

def save_tweets(tweets, tweet_path:str):
    with open(tweet_path, 'w') as f:
        json.dump(tweets, f)

def extract_info(tweets:list)->list:
    return [
        {
            "id": tweet["tweet"]["id"], 
            "text": tweet["tweet"]["full_text"],
            "created_at": tweet["tweet"]["created_at"],
        } for tweet in tweets
    ]
def parse_tweet_date(tweet):
    return datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')

def get_tweet_text(tweet):
    return tweet['text']

def get_tweets_by_date(tweets:list, start_date, end_date=None)->list:
    start_date = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        
    if end_date is None:
        end_date = start_date + timedelta(days=1)
    else:
     end_date = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    
    filtered_tweets = [
            tweet for tweet in tweets
            if start_date <=parse_tweet_date(tweet)<= end_date
        ]

    return filtered_tweets

def divide_tweets_by_period(tweets: list, period_days: int) -> list:
    """
    Divide tweets into sections by time period and return a list of them.

    :param tweets: List of tweet dictionaries
    :param period_days: Number of days for each period
    :return: List of sections, each containing tweets for the specified period
    """
    
    # Sort tweets by creation date
    sorted_tweets = sorted(tweets, key=parse_tweet_date)
    
    # Initialize variables
    sections = []
    current_section = []
    current_period_start = parse_tweet_date(sorted_tweets[0])
    period_timedelta = timedelta(days=period_days)
    
    # Iterate through sorted tweets and divide them into sections
    for tweet in sorted_tweets:
        tweet_date = parse_tweet_date(tweet)
        if tweet_date < current_period_start + period_timedelta:
            current_section.append(tweet)
        else:
            sections.append(current_section)
            current_section = [tweet]
            current_period_start = tweet_date
            
    # Append the last section
    if current_section:
        sections.append(current_section)
    
    return sections
    

def divide_tweets_by_period_text(tweets: list, period_days: int) -> list:
    """
    Divide tweets into sections by time period and return a list of strings.

    :param tweets: List of tweet dictionaries
    :param period_days: Number of days for each period
    :return: List of strings, each containing tweets for the specified period
    """
    
    # Sort tweets by creation date
    sorted_tweets = sorted(tweets, key=parse_tweet_date)
    
    # Initialize variables
    sections = []
    current_section = []
    current_period_start = parse_tweet_date(sorted_tweets[0])
    period_timedelta = timedelta(days=period_days)
    
    # Iterate through sorted tweets and divide them into sections
    for tweet in sorted_tweets:
        tweet_date = parse_tweet_date(tweet)
        if tweet_date < current_period_start + period_timedelta:
            current_section.append(tweet['text'])
        else:
            sections.append("\n ".join(current_section))
            current_section = [tweet['text']]
            current_period_start = tweet_date
            
    # Append the last section
    if current_section:
        sections.append("\n ".join(current_section))
    
    return sections
