import tweepy
import webbrowser
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

#variables
positive = 0
negative = 0
neutral = 0
polarity = 0
list_items = []
f = open('credential.json')
data = json.load(f)

positive_tweets = 0
negative_tweets = 0
neutral_tweets = 0

 #Access tokens & secure access
    
api_key = data['API_Key']
api_secret_key = data['API_SecretKey']
access_token = data['Access_Token']
access_token_secret = data['Access_TokenSecret']

#Fetching tweets of some users

screenname = input('Enter a name:- ')
no_of_tweets = int(input('Enter the number of Tweets:- '))
new_name = screenname.replace(" ","")



#Establishing secure connection
auth = tweepy.OAuthHandler(api_key,api_secret_key)
auth.set_access_token(access_token,access_token_secret)
api = tweepy.API(auth)


try:
    i = 1     
    for posts in tweepy.Cursor(api.home_timeline, screen_name = new_name).items(no_of_tweets):
        print(str(i) + ')' + posts.text + '\n')
        i = i + 1
        analysis = TextBlob(posts.text)

        if(analysis.sentiment.polarity == 0):
            print('Neutral' + '\n')
            neutral_tweets += 1
        elif(analysis.sentiment.polarity < 0):
            print('Negative' + '\n')
            negative_tweets += 1
        elif(analysis.sentiment.polarity > 0):
            print('Positive' + '\n')
            positive_tweets += 1

   
        # print(str(i) + ')' + tweet.full_text + '\n')
        # i = i+1
except tweepy.TweepError as ex:
     if ex.reason == "Not authorized.":
            print('User Tweets Cannot Be fetched')


print('No of neutral tweets :- '+ str(neutral_tweets) + '\nNo of negative tweets :- '+ str(negative_tweets) + '\nNo of positive tweets :-' +str(positive_tweets))




# me = api.me()
# print(me.screen_name)

