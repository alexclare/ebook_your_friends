from twython import Twython, TwythonError
from markov import MarkovGenerator, twitter_tokenize
from math import log
from random import random
import argparse
import os
import time

APP_KEY = os.getenv('APP_KEY')
APP_SECRET = os.getenv('APP_SECRET')
OAUTH_TOKEN = os.getenv('OAUTH_TOKEN')
OAUTH_TOKEN_SECRET = os.getenv('OAUTH_TOKEN_SECRET')

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

'''time between tweets in seconds
set a minimum because we don't want near-simultaneous tweets'''
minimum_interval = 300
average_interval = 7200


def get_tweets(username):
    '''(str) -> list of tweets,
    fetches last 200 tweets from specified user'''
    try:
        user_timeline = twitter.get_user_timeline(
            screen_name=username, count=200, include_rts=False, exclude_replies=True)
        tweets = [user_timeline[i]['text']
                  for i in range(len(user_timeline) - 1)]
        return tweets
    except TwythonError as e:
        print e
        return e


def generate_status(tweet_list):
    '''(list) -> str,
    returns markov-generated status'''
    tweet_text = ' '.join(tweet_list)
    try:
        mc = MarkovGenerator(tweet_text, 90, tokenize_fun=twitter_tokenize)
        status = mc.generate_words().lower()
        return status
    except ValueError as e:
        print e


def ebook(user, dry_run=False):
    '''posts generated status to twitter'''
    status = generate_status(get_tweets(user))
    try:
        if not dry_run:
            twitter.update_status(status=status)
        print time.strftime('[%y-%m-%dT%H:%M:%S] {}').format(status)
        time.sleep(minimum_interval -
                   log(random()) * (average_interval - minimum_interval))
    except TwythonError as e:
        print e


def main():
    parser = argparse.ArgumentParser(description='ebook your friends!!!')
    parser.add_argument('user', action='store', help='the user who you want to "ebook"')
    parser.add_argument('--dry-run', action='store_true',
                        help="run the bot logic but don't actually tweet; " +
                        "still connects to Twitter to fetch existing tweets")
    args = parser.parse_args()
    while True:
        ebook(args.user, args.dry_run)


if __name__ == '__main__':
    main()
