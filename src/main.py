from matplotlib.pyplot import get
import metric, data
from typing import Optional

def get_coordinates(word:str, provider:str, tweet_path:str, start_date:Optional[str] = None, end_date:Optional[str] = None):
    tweets = data.load_tweets(tweet_path)
    extracted = data.extract_info(tweets)
    if(start_date != None and end_date !=None):
        extracted = data.get_tweets_by_date(extracted, start_date, end_date)
    tweet_text = data.divide_tweets_by_period_text(extracted, 80)
    
    model = metric.load_model(provider=provider)
    is_slang = metric.is_slang(model, word)
    
    attributes = metric.create_words(model, word, is_slang = is_slang)
    ratings = []
    for text in tweet_text:
        ratings.append(metric.give_rating(text, model, word, attributes['x_meaning'], attributes['positive_x'], attributes['negative_x'], attributes['y_meaning'], attributes['positive_y'], attributes['negative_y']))
    
    mean_x = sum(rating[0] for rating in ratings) / len(ratings)
    mean_y = sum(rating[1] for rating in ratings) / len(ratings)
    mean_rating = (mean_x, mean_y)


    #del model
    return mean_rating, attributes

#word = "kino"
#provider = "llama_cpp"
#tweet_path = "../data/tweets.json"
#rating, attributes = get_coordinates(word, provider, tweet_path)
#print(rating)
