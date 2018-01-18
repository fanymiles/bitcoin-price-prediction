import re
import time
import json
import tweepy
import atexit
import logging
import datetime
import schedule
import argparse
from textblob import TextBlob
from kafka import KafkaProducer

# logging config
logging.basicConfig()
logger = logging.getLogger('fetch-sentiment')
logger.setLevel(logging.DEBUG)


class TwitterClient(object):
    '''
    Generic Twitter Class for sentiment analysis.
    '''
    def __init__(self):
        '''
        Class constructor or initialization method.
        '''
        # set twitter api credentials
        consumer_key= 'MOe623rxcqck6x8y5XhzK8MJT'
        consumer_secret= 'mcBq9Km1f3OYERRD6vKmOfWSgCjsqzXAreIsn8klxAtPIo40E7'
        access_token='913787859630460928-RXF8NVN3gGbxD64NCZ7wBma5M2WPwlv'
        access_token_secret='P4UU9I2DimdnUown2EM6p4WZ0ftdPNsysDNW6xGh0Ts4f'
        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        return analysis.sentiment.polarity

    def send_to_kafka(self, data, producer, topic_name):
        # send the data to kafka
        try:
            logger.info(data)
            producer.send(topic=topic_name, value=data)
            logger.debug('sent data to kafka')
        except Exception as e:
            logger.warn('failed to send price to kafka')

    def get_sentiments_and_send(self, producer, topic_name, query, count = 100):
        # run polarity analysis on tweets
        sentiments = 0
        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(q = query, count = count)
            for tweet in fetched_tweets:
                sentiments += self.get_tweet_sentiment(tweet.text) * 1.0 / count
            data = {
                'timestamp':datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                'sentiment': sentiments
            }
            self.send_to_kafka(json.dumps(data), producer, topic_name)
        except tweepy.TweepError as e:
            # log error (if any)
            logger.error("Error : " + str(e))

    def get_tweets(self, query, count = 100):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        positive = 0
        negative = 0
        ptweet = ""
        ntweet = ""

        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(q = query, count = count)

            # parsing tweets one by one
            for tweet in fetched_tweets:
                sentiment = self.get_tweet_sentiment(tweet.text)
                # saving sentiment of tweet
                if(sentiment > 0):
                    positive += 1
                    if positive == 1:
                        ptweet = tweet.text
                elif(sentiment < 0):
                    negative += 1
                    if negative == 1:
                        ntweet = tweet.text
            # return a posive tweet, a negative tweet, the positive tweet percent and the negative tweet percent 
            results = {
                "positive_tweet": ptweet,
                "negative_tweet": ntweet,
                "positive_percentage": positive / 100.0,
                "negative_percentage": negative / 100.0,
                "neutral_percentage": (100 - positive - negative) / 100.0
            }
            return results

        except tweepy.TweepError as e:
            # log error (if any)
            logger.error("Error : " + str(e))
        
    def shutdown_hook(self, producer):
        logger.info('closing kafka producer')
        producer.flush(10)
        producer.close(10)
        logger.info('kafka producer closed')
 
def main():
    # creating object of TwitterClient Class
    api = TwitterClient()
    # calling function to get tweets about bitcoin
    tweets = api.get_tweets(query = 'bitcoin, price, crypto')
    # printing a positive tweet
    print "\n\nPositive tweets: \n%s" % tweets["positive_tweet"]
    # printing a negative tweet
    print "\n\nNegative tweets: \n%s\n" % tweets["negative_tweet"]
    print "Positive tweets percentage: {}%".format(100*tweets["positive_percentage"])
    print "Negative tweets percentage: {}%".format(100*tweets["negative_percentage"])
    print "Neutral tweets percentage: {}%".format(100*tweets["neutral_percentage"])

    #parse argument from driver
    parser = argparse.ArgumentParser()
    parser.add_argument('topic_name', help='the name of the topic') 
    parser.add_argument('kafka_broker', help='the location of the kafka')
    args = parser.parse_args()
    topic_name = args.topic_name
    kafka_broker = args.kafka_broker
    producer = KafkaProducer(
        bootstrap_servers=kafka_broker
    )

    # fetch sentiments by schedule 
    schedule.every(1).second.do(api.get_sentiments_and_send, producer, topic_name, query=['bitcoin, price, crypto'], count=100)

    # shutdown hook at exit
    atexit.register(api.shutdown_hook, producer)

    while True:
        schedule.run_pending()

if __name__ == "__main__":
    # calling main function
    main()

