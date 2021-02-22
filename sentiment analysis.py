from tweepy import OAuthHandler, API, Cursor, TweepError, RateLimitError, Stream
from tweepy.streaming import StreamListener
import pandas as pd
from datetime import datetime
import time
import json
import os
import keys_token as key

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

auth = OAuthHandler(key.CONSUMER_KEY, key.CONSUMER_SECRET_KEY)
auth.set_access_token(key.ACCESS_TOKEN, key.ACCESS_SECRET_TOKEN)
api = API(auth, wait_on_rate_limit=False, wait_on_rate_limit_notify=False)

def fetch_tweets(search_key):
    os.mkdir(f'./{search_key}')
    cursor = Cursor(api.search, q=f'#{search_key} -filter:retweets',
                    count=100, tweet_mode='extended').items(15000)

    df = pd.DataFrame()

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
            df = pd.concat([df, pd.DataFrame([row], index=[i])])
        except TweepError:
            break
        except RateLimitError:
            break
        except StopIteration:
            break
        i = i + 1

    df = df.sort_values(by=['like_count', 'retweet_count', 'followers_count'], ascending=False)
    df.to_csv(path_or_buf=f'./{search_key}/{search_key}.csv')
    df['screen_name'].value_counts().to_csv(path_or_buf=f'./{search_key}/screen_name_freq.csv')
    print('\nCompleted.')

class listener(StreamListener):
    def __init__(self, api=None):
        super().__init__(api=api)
        self.count = 1

    def on_exception(self, exception):
        global df
        print(exception)
        df = df.sort_values(by=['like_count', 'retweet_count', 'followers_count'], ascending=False)
        df.to_csv(path_or_buf='./data.csv')
        print('\nCompleted.')
        return False

    def on_status(self, status):
        return super().on_status(status)
    
    def on_data(self, tweet):
        global df
        tweet = json.loads(tweet)
        if not tweet['retweeted'] and 'RT @' not in tweet['text']:
            print(f'Running... {self.count}\r', end='')
            row = {
                'tweet_id': tweet['id'],
                'screen_name': tweet['user']['screen_name'],
                'name': tweet['user']['name'],
                'tweet_date': datetime_from_utc_to_local(datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')),
                'location': tweet['user']['location'],
                'retweet_count': tweet['retweet_count'],
                'comment_count': tweet['reply_count'],
                'quote_count': tweet['quote_count'],
                'like_count': tweet['favorite_count'],
                'followers_count': tweet['user']['followers_count'],
                'following_count': tweet['user']['friends_count'],
                'text': tweet['text'],
                'embed_url': f'https://twitter.com/{tweet["user"]["screen_name"]}/status/{tweet["id"]}?s=20'
            }
            df = pd.concat([df, pd.DataFrame([row], index=[self.count])])
            self.count = self.count + 1
            return True

    def on_error(self, status):
        global df
        print(status)
        df = df.sort_values(by=['like_count', 'retweet_count', 'followers_count'], ascending=False)
        df.to_csv(path_or_buf='./data.csv')
        print('\nCompleted.')
        return False

fetch_tweets(input('Enter search key: '))

df = pd.DataFrame()
# stream = Stream(auth=api.auth, listener=listener(), tweet_mode='extended')
# stream.filter(track=['Tesla', 'Bitcoin'], is_async=True)

# for i, tweet in enumerate(tweets):
#     try:
#         tweet_info = tweet._json
#         entities_info = tweet.entities
#         user_info = tweet.user._json
#         print(f'{i + 1}')
#         print_dict(tweet_info)
#         print_dict(entities_info)
#         print_dict(user_info)
#     except TweepError:
#         time.sleep(60 * 15)
#         continue