#!/usr/bin/env python
#requirement BeautifulSoup (http://www.crummy.com/software/BeautifulSoup)
# get it via pip install beautifulsoup4
from bs4 import BeautifulSoup
from datetime import datetime
from subprocess import call
import requests
import os.path
from time import sleep
import sys


def read_new_tweets(twitter_accountname):

    url = "http://twitter.com/" + twitter_accountname
    doc = requests.get(url)

    #write backup
    myfile = open(twitter_accountname + '.html', 'w')
    myfile.write(doc.text)
    myfile.close()

    #parse html
    soup = BeautifulSoup(doc.text, 'html.parser')
    lots = []
    rows = soup.select(".js-stream-tweet")

    if len(rows) > 0:
        for row in rows:
            tweet_timestamp = int(row.select(".js-short-timestamp")[0]['data-time'])
            tweet_text = row.select(".js-tweet-text")
            if len(tweet_text) > 0:
                tweet_text = tweet_text[0].text
                lots.append((tweet_timestamp, tweet_text))
    else:
        print("No tweets found in HTML")
    return lots

def read_old_tweets(twitter_accountname):
    tweet_list = []
    my_filename = twitter_accountname + ".csv"
    if os.path.isfile(my_filename):
        with open(my_filename, 'r') as myfile:
            for curline in myfile:
                pos_of_comma = curline.find(',')
                if pos_of_comma > -1:
                    tweet_timestamp = int(curline[0:pos_of_comma])
                    tweet_text = curline[pos_of_comma + 1:]
                    tweet_list.append((tweet_timestamp, tweet_text))
    return tweet_list

def diff_on_tweet_list(old_tweet_list, new_tweet_list):
    list_not_in_old_tweets = []
    for cur_new_tweet in new_tweet_list:
        found_in_both = False
        for cur_old_tweet in old_tweet_list:
            if cur_old_tweet[0] == cur_new_tweet[0]:
                found_in_both = True
                break
        if not found_in_both:
            list_not_in_old_tweets.append(cur_new_tweet)

    return list_not_in_old_tweets

def write_tweets(twitter_accountname, list_of_tweets):
    with open(twitter_accountname + ".csv", 'w') as tweet_file:
        for cur_tweet in list_of_tweets:
            tweet_file.write(str(cur_tweet[0]) + "," + cur_tweet[1])
            if cur_tweet[1].rfind("\n") < (len(cur_tweet[1]) - 1):
                tweet_file.write("\n")

def notify_about_new_tweets(list_of_new_tweets):
    for cur_tweet in list_of_new_tweets:
        cur_delay = 5000 + int(len(cur_tweet[1]) / 40)
        tweet_timestr = datetime.fromtimestamp(cur_tweet[0]).strftime("%d. %b %H:%I:%S")
        notify_text = tweet_timestr + ":\n" + cur_tweet[1] 
        call(["notify-send", "-c", "low", "-t", str(cur_delay), "-i", "apple-touch-icon.png", notify_text ])
        print("Notification:" + notify_text)
        sleep(cur_delay / 1000)


def main(twitter_accountname):

    current_tweets = read_new_tweets(twitter_accountname)

    old_tweets = read_old_tweets(twitter_accountname)

    list_of_new_tweets = diff_on_tweet_list(old_tweets, current_tweets)

    write_tweets(twitter_accountname, old_tweets + list_of_new_tweets)

    if len(list_of_new_tweets) > 0:
        notify_about_new_tweets(list_of_new_tweets)
#    for name, free_lots in lots:
#        print("%s: %s" % (name, free_lots))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Twitter accountname required. None given. Aborting.")

