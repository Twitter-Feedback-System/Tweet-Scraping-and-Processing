import json
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import tweepy
import re

tweets = {}
tweet_list = []
regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
f = open('credential.json')
f2 = open('new.txt','a')
data = json.load(f)
api_key = data['API_Key']
api_secret_key = data['API_SecretKey'] 
access_token = data['Access_Token']
access_token_secret = data['Access_TokenSecret']

auth = tweepy.OAuthHandler(api_key,api_secret_key)
auth.set_access_token(access_token,access_token_secret)
auth.secure = True
api = tweepy.API(auth,wait_on_rate_limit = True,wait_on_rate_limit_notify = True)

searchQuery = input('Enter a keyword:- ')
tweetsToSearch = int(input('Enter the number of tweets:- '))
 
i =1
for tweet in tweepy.Cursor(api.home_timeline,screen_name = searchQuery).items(tweetsToSearch):
    dict_tweets = dict()
    tweets = tweet
    dict_tweets['text'] = tweets.text.encode('utf-8')
    tweet_list.append(dict_tweets)

for a in tweet_list:
    clean_tweet = a['text'].decode('utf-8')
    clean_tweet = re.sub(r'^RT[\s]+','',clean_tweet)
    clean_tweet = re.sub(r'https?:\/\/.*[\r\n]*', '', clean_tweet)
    clean_tweet = re.sub(r'#', '', clean_tweet)
    clean_tweet = re.sub(r'@[A-Za-z0–9]+', '', clean_tweet)
    clean_tweet = regrex_pattern.sub(r'',clean_tweet)
    clean_tweet = re.sub('\n',' ',clean_tweet)
    a['text'] = clean_tweet 

for a in tweet_list:
    print(str(i) + ')' + a['text'] + '\n')
    i = i + 1
# with open('new.json','w') as outfile:
#     json.dump(tweet_list,outfile)
