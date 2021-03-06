from tweepy import OAuthHandler, API, Cursor, TweepError, RateLimitError, Stream
from textblob import TextBlob
import pandas as pd
from datetime import datetime
import time
# import json
import os
import re
import concurrent.futures
import keys_token as key

neutral_tweets, negative_tweets, positive_tweets = 0, 0, 0

# https://stackoverflow.com/questions/4770297/convert-utc-datetime-string-to-local-datetime
def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(
        now_timestamp)
    return utc_datetime + offset

def print_dict(obj):
    keys = ['entities', 'user']
    for key, value in obj.items():
        if key not in keys:
            print(f'\t{key}: {value}')

def print_response(text):
    global neutral_tweets, negative_tweets, positive_tweets
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)

    clean_tweet = text.decode('utf-8')
    clean_tweet = re.sub(r'^RT[\s]+','', clean_tweet)
    clean_tweet = re.sub(r'https?:\/\/.*[\r\n]*', '', clean_tweet)
    clean_tweet = re.sub(r'#', '', clean_tweet)
    clean_tweet = re.sub(r'@[A-Za-z0–9]+', '', clean_tweet)
    clean_tweet = regrex_pattern.sub(r'', clean_tweet)
    clean_tweet = re.sub('\n',' ', clean_tweet)

    analysis = TextBlob(clean_tweet)
    if(analysis.sentiment.polarity == 0):
        neutral_tweets += 1
    elif(analysis.sentiment.polarity < 0):
        negative_tweets += 1
    elif(analysis.sentiment.polarity > 0):
        positive_tweets += 1

def fetch_tweets(search_key, api):
    os.mkdir(f'./{search_key}')
    os.mkdir(f'./{search_key}/images')
    os.mkdir(f'./{search_key}/images/top_users')
    os.mkdir(f'./{search_key}/images/trends')

    cursor = Cursor(api.search, q=f'#{search_key} -filter:retweets',
                    count=100, tweet_mode='extended', lang='en').items(500)

    df = pd.DataFrame()
    screen_name_df = pd.DataFrame(columns=['screen_name', 'no. of tweets'])

    i = 1
    while True:
        print(f'Running... {i}\r', end='')
        try:
            tweet = cursor.next()
            row = {
                'tweet_id': tweet.id,
                'screen_name': tweet.user.screen_name,
                'name': tweet.user.name,
                'tweet_date': datetime_from_utc_to_local(tweet.created_at),
                'location': tweet.user.location,
                'retweet_count': tweet.retweet_count,
                'like_count': tweet.favorite_count,
                'followers_count': tweet.user.followers_count,
                'following_count': tweet.user.friends_count,
                'text': tweet.full_text or tweet.text,
                'embed_url': f'https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}?s=20'
            }
            new_rows = pd.DataFrame([row], index=[i])
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                executor.submit(print_response, row['text'].encode('utf-8'))
                # executor.map(print_response, row['text'].encode('utf-8'))
            # print_response(row['text'].encode('utf-8'))
            df = pd.concat([df, new_rows])
        except TweepError:
            break
        except RateLimitError:
            break
        except StopIteration:
            break
        i = i + 1

    df = df.sort_values(by=['like_count', 'retweet_count', 'followers_count'], ascending=False)
    df.to_csv(path_or_buf=f'./{search_key}/{search_key}.csv')
    screen_name_df = df['screen_name'].value_counts().rename_axis('screen_name').to_frame(name='no. of tweets')
    top_10_freq_users = screen_name_df.head(10)
    tweet_trend_df = df['tweet_date'].value_counts().rename_axis('date').to_frame(name='count').sort_values(by='date')
    
    screen_name_df.to_csv(path_or_buf=f'./{search_key}/screen_name_freq.csv')
    top_10_freq_users.plot(kind='pie', figsize=(30, 20), fontsize=26, y='no. of tweets').get_figure().savefig(f'./{search_key}/images/top_users/no_of_tweets.jpg')
    top_10_freq_users.plot(kind='pie', figsize=(30, 20), fontsize=26, y='no. of tweets').get_figure().savefig(f'./{search_key}/images/top_users/no_of_tweets.png')
    top_10_freq_users.plot(kind='pie', figsize=(30, 20), fontsize=26, y='no. of tweets').get_figure().savefig(f'./{search_key}/images/top_users/no_of_tweets.svg')
    top_10_freq_users.plot(kind='pie', figsize=(30, 20), fontsize=26, y='no. of tweets').get_figure().savefig(f'./{search_key}/images/top_users/no_of_tweets.pdf')

    tweet_trend_df.to_csv(path_or_buf=f'./{search_key}/trend.csv')
    tweet_trend_df.plot(kind='line', figsize=(70, 50), fontsize=26).get_figure().savefig(f'./{search_key}/images/trends/trend.jpg')
    tweet_trend_df.plot(kind='line', figsize=(70, 50), fontsize=26).get_figure().savefig(f'./{search_key}/images/trends/trend.png')
    tweet_trend_df.plot(kind='line', figsize=(70, 50), fontsize=26).get_figure().savefig(f'./{search_key}/images/trends/trend.svg')
    tweet_trend_df.plot(kind='line', figsize=(70, 50), fontsize=26).get_figure().savefig(f'./{search_key}/images/trends/trend.pdf')

    print('\nCompleted.')

if __name__ == '__main__':    
    auth = OAuthHandler(key.CONSUMER_KEY, key.CONSUMER_SECRET_KEY)
    auth.set_access_token(key.ACCESS_TOKEN, key.ACCESS_SECRET_TOKEN)
    api = API(auth, wait_on_rate_limit=False, wait_on_rate_limit_notify=False)
    fetch_tweets(input('Enter search key: '), api)
    print(f'positive: {positive_tweets}\nneutral: {neutral_tweets}\nnegative: {negative_tweets}')

# class listener(StreamListener):
#     def __init__(self, api=None):
#         super().__init__(api=api)
#         self.count = 1

#     def on_exception(self, exception):
#         global df
#         print(exception)
#         df = df.sort_values(by=['like_count', 'retweet_count', 'followers_count'], ascending=False)
#         df.to_csv(path_or_buf='./data.csv')
#         print('\nCompleted.')
#         return False

#     def on_status(self, status):
#         return super().on_status(status)
    
#     def on_data(self, tweet):
#         global df
#         tweet = json.loads(tweet)
#         if not tweet['retweeted'] and 'RT @' not in tweet['text']:
#             print(f'Running... {self.count}\r', end='')
#             row = {
#                 'tweet_id': tweet['id'],
#                 'screen_name': tweet['user']['screen_name'],
#                 'name': tweet['user']['name'],
#                 'tweet_date': datetime_from_utc_to_local(datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')),
#                 'location': tweet['user']['location'],
#                 'retweet_count': tweet['retweet_count'],
#                 'comment_count': tweet['reply_count'],
#                 'quote_count': tweet['quote_count'],
#                 'like_count': tweet['favorite_count'],
#                 'followers_count': tweet['user']['followers_count'],
#                 'following_count': tweet['user']['friends_count'],
#                 'text': tweet['text'],
#                 'embed_url': f'https://twitter.com/{tweet["user"]["screen_name"]}/status/{tweet["id"]}?s=20'
#             }
#             df = pd.concat([df, pd.DataFrame([row], index=[self.count])])
#             self.count = self.count + 1
#             return True

#     def on_error(self, status):
#         global df
#         print(status)
#         df = df.sort_values(by=['like_count', 'retweet_count', 'followers_count'], ascending=False)
#         df.to_csv(path_or_buf='./data.csv')
#         print('\nCompleted.')
#         return False
