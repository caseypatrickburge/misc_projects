### Import Necessary Modules / Libraries ###
from django.shortcuts import render, redirect
import os
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import json 
from django.http import JsonResponse
from . import secrets

# import sentiment analysis modules
import spacy
# import en_core_web_sm
import vaderSentiment.vaderSentiment as vader

# import tweet crawler modules
import tweepy
import csv
import numpy as np
import pandas as pd

# import visualization modules
import nltk
import matplotlib.pyplot as plt
from wordcloud import WordCloud 
import matplotlib.pyplot as plt; plt.rcdefaults()

def analyze(request):
    print(request.POST)
    if request.method == 'POST':
        q = request.POST.get('q')
        count = request.POST.get('count')
        month = request.POST.get('month')
        day = request.POST.get('day')
        year = request.POST.get('year')
        return render(request, "home.html", {
            'q':q,
            'count':count,
            'year':year,
            'month':month,
            'day':day,
        })
    return render(request, 'search.html')    
    
@csrf_exempt
def sentiment_return(request):
    data = json.loads(request.body)
    print(data)
    q = data["query"]
    month = "01"
    day = "01"
    year = "2020"
    count = "2"
    # delete previous wordcloud
    try:
        os.remove("static/wordcloud.png")
    except FileNotFoundError:
        pass   
    try: 
        os.remove("static/bar.png")
    except FileNotFoundError:
        pass
    # function that pulls tweets
    def get_tweets():
    # twitter dev credentials here:
        consumer_key = 'sDWaGkbuFxWBWIjlcDziP9Y3K'
        consumer_secret = 'TipNqpxvHD4D9MsrhzNH5BGszEXym7VF6gxBR5MFhkIY7fdjKy'
        access_token = '1218694128260640768-zI3bHLIW4uPtfwHfVhVCW3dozU57pj'
        access_token_secret = 'kvKjWAYQYEso2MuMGEtEYnRHWPVwMnf1XyJy6tzR7VW5V'

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

        # open/create a file to append data
        # csvFile = open('tweets.csv', 'a')
        # # use csv Writer
        # csvWriter = csv.writer(csvFile)

        # compile tweets csv to be analyzed
        tweet_array = []
        for tweet in tweepy.Cursor(api.search,q=f"{q}",count=f"{count}",
                                lang="en",
                                since=f"{year}-{month}-{day}").items():
            # print (tweet.created_at, tweet.text)
            tweet_array.append({"created": tweet.created_at, "body": tweet.text.encode('utf-8')})
            # csvWriter.writerow([tweet.created_at, tweet.text.encode('utf-8')])
        return tweet_array

        
    # call get_tweets()
    tweet_list = get_tweets()

    # sentiment analysis function 
    analyzer = vader.SentimentIntensityAnalyzer()
    english = spacy.load("en_core_web_sm")

    # define get_sentiments function to process tweets
    def get_sentiments(text_list):
        text = "\n".join([str(tweet["body"]) for tweet in text_list])
        result = english(text)
        # print(result)
        sentences = [str(sent) for sent in result.sents]
        sentiments = [analyzer.polarity_scores(str(s)) for s in sentences]
        return sentiments    

    # define analyze_tweets function
    def analyze_tweets(tweet_list):
        # open and analyze sentiment of tweets
        # data = open('tweets.csv', 'r')
        # text = data.read()
        text = tweet_list
        sentiments = get_sentiments(text)

        # open/create a file to append data
        csvFile = open('sentiment.csv', 'a')
        fieldnames = ["neg", "neu", "pos", "compound"]
        # use csv Writer
        csvWriter = csv.DictWriter(csvFile, fieldnames=fieldnames)

        # compile tweets csv to be analyzed
        csvWriter.writeheader()
        for sent in sentiments:
            # print(sent)
            csvWriter.writerow(sent)

    analyze_tweets(tweet_list)

    def find_sent_mean():
        df = pd.read_csv("sentiment.csv")
        mean = df.mean()
        mean = mean.drop(["neu", "compound"])
        neg = float(mean[0]) * 100
        pos = float(mean[1]) * 100
        neg = format(neg,'.1f')
        pos = format(pos,'.1f')
        print("\n----------- Tweet Sentiment -----------\n")
        print(f"Negative: {neg}\nPositive: {pos}")
        os.remove("sentiment.csv")
        return neg, pos
    # call find_sent_mean function
    neg, pos = find_sent_mean()
    # define generate_wordcloud function
    def generate_wordcloud(tweet_list):
        # define now for naming wordcloud.png
        now = datetime.now()
        # create wordcloud from tweet_list
        # remove stopwords & irrelevant phrases
        WordCloud(background_color="white", max_words=5000, contour_width=3, contour_color="steelblue").generate_from_text(" ".join([r for _d in tweet_list for r in _d['body'].decode('utf-8').replace('https', "").replace('photo', '').replace('RT', '').split() if r not in set(nltk.corpus.stopwords.words("english"))])).to_file("static/wordcloud.png")
        
    generate_wordcloud(tweet_list)

    def generate_bar():
        positive = pos
        negative = neg
        objects = ('Positive', 'Negative')
        y_pos = np.arange(len(objects))
        performance = [positive,negative]

        plt.bar(y_pos, performance, align='center', alpha=0.5)
        plt.xticks(y_pos, objects)
        plt.ylabel('Sentiment Score')
        plt.title('')
        plt.savefig('static/bar.png')
    generate_bar()    
    
    return JsonResponse({
        "neg":neg,
        "pos":pos,
        "q":q,
    })

