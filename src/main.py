import metric, data
import json
import time
import os
import matplotlib.pyplot as plt
from rich import print

start = time.time()

tweet_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'tweets.json')
tweets = data.load_tweets(tweet_path)
extracted = data.extract_info(tweets)

start_date = '2024-06-27'
end_date = '2024-06-28'
# filtered_tweets = data.get_tweets_by_date(extracted, start_date, end_date)
tweet_text = data.divide_tweets_by_period_text(extracted,80)


model = metric.load_model()
# chunks = metric.chunk_text(tweet_text[0], max_chars=4000, overlap=100)

word = "tech bro"
is_slang = metric.is_slang(model, word)

attributes = metric.create_words(model, word, is_slang = is_slang)
ratings = []
for text in tweet_text:
    ratings.append(metric.give_rating(text, model, word, attributes['x_meaning'], attributes['positive_x'], attributes['negative_x'], attributes['y_meaning'], attributes['positive_y'], attributes['negative_y']))

 

mean_x = sum(rating[0] for rating in ratings) / len(ratings)
mean_y = sum(rating[1] for rating in ratings) / len(ratings)
mean_rating = (mean_x, mean_y)

del model

# Create the plot
plt.figure(figsize=(8, 8))

# Plot individual ratings
for rating in ratings:
    plt.scatter(rating[0], rating[1], c='blue', s=50, label='Individual Rating' if rating == ratings[0] else "")

# Plot the mean rating
plt.scatter(mean_rating[0], mean_rating[1], c='red', s=100, label='Mean Rating')  # Larger red dot for the mean rating

end = time.time()
print(f"[bold green] Mean rating: [/] [yellow]{end - start} [/][bold green]seconds[/]")
print(f"[bold green] Mean rating: [/] [yellow]{mean_rating}[/]")
# Label the axes
plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(0, color='black', linewidth=0.5)
plt.grid(which='both', color='grey', linestyle='-', linewidth=0.25, alpha=0.5)

plt.xlabel(f"{attributes['negative_x']} <--- {attributes['x_meaning']} ---> {attributes['positive_x']}")
plt.ylabel(f"{attributes['negative_y']} <--- {attributes['y_meaning']} ---> {attributes['positive_y']}")

# Set the limits for x and y axes
plt.xlim(-8, 8)
plt.ylim(-8, 8)

# Show the plot with legend
plt.title("Techbro Ratings on Knowledge Level and Social Awareness")
plt.legend()
plt.show()