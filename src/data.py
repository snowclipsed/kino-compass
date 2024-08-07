import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict

def load_tweets(tweet_path:str):
    """
    This function loads tweets from a JSON file.
    """
    with open(tweet_path) as f:
        return json.load(f)

def save_tweets(tweets, tweet_path:str):
    """
    This function saves tweets to a JSON file.
    """
    with open(tweet_path, 'w') as f:
        json.dump(tweets, f)

def extract_info(tweets:List)->List:
    """
    This function extracts the tweet id, text, and creation date from a list of tweet dictionaries.
    ----------
    Args:
        tweets: List - List of tweet dictionaries
    Returns:
        extracted_tweets: List - List of dictionaries with 'id', 'text', and 'created_at' keys
    """
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

def get_tweets_by_date(tweets:List, start_date, end_date=None)->List:
    """
    This function filters tweets based on the start and end date.
    If no end date is provided, the function will filter tweets for the specified start date only.
    ----------
    Args:
        tweets: List - List of tweet dictionaries
        start_date: str - Start date in the format 'YYYY-MM-DD'
        end_date: str - End date in the format 'YYYY-MM-DD'
    Returns:
        filtered_tweets: List - List of filtered tweets
    """
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

def divide_tweets_by_period(tweets: List, period_days: int) -> List:
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
    

def divide_tweets_by_period_text(tweets: List[Dict], period_days: int) -> List[str]:
    """
    Divide tweets into sections by time period and return a list of strings.

    :param tweets: List of tweet dictionaries
    :param period_days: Number of days for each period
    :return: List of strings, each containing tweets for the specified period
    :raises ValueError: If tweets is not a list, period_days is not a positive integer, or tweets are improperly formatted
    """
    if not isinstance(tweets, list):
        raise ValueError("tweets must be a list")
    if not all(isinstance(tweet, dict) and 'created_at' in tweet and 'text' in tweet for tweet in tweets):
        raise ValueError("Each tweet must be a dictionary with 'created_at' and 'text' keys")
    if not isinstance(period_days, int) or period_days <= 0:
        raise ValueError("period_days must be a positive integer")
    if not tweets:
        return []

    try:
        # Sort tweets by creation date
        sorted_tweets = sorted(tweets, key=parse_tweet_date)
    except Exception as e:
        raise ValueError(f"Error parsing tweet dates: {e}")

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
            sections.append("\n".join(current_section))
            current_section = [tweet['text']]
            current_period_start = tweet_date

    # Append the last section
    if current_section:
        sections.append("\n".join(current_section))

    return sections
