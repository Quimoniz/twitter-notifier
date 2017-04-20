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
    """fetchtes tweets from twitter.com and puts timestamp and tweettext into an array."""
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

def escape_str(orig_str):
    escaped_str = []
    for cur_char in orig_str:
        if "\n" == cur_char:
            escaped_str.append('\\')
            escaped_str.append("n")
        elif "\\" == cur_char:
            escaped_str.append('\\')
            escaped_str.append('\\')
        else:
            escaped_str.append(cur_char)
    return ''.join(escaped_str)

def unescape_str(orig_str):
    unescaped_str = []
    encountered_backslash = False
    for cur_char in orig_str:
        if encountered_backslash:
            if "n" == cur_char:
                unescaped_str.append("\n")
            elif "\\" == cur_char:
                unescaped_str.append("\\")
            else:
                unescaped_str.append("\\")
                unescaped_str.append(cur_char)
            encountered_backslash = False
        else:
            if "\\" == cur_char:
                encountered_backslash = True
            else:
                unescaped_str.append(cur_char)
    return ''.join(unescaped_str)
       

def read_old_tweets(twitter_accountname):
    """reads in the corresponding .csv file and returns an array with the read data"""
    tweet_list = []
    my_filename = twitter_accountname + ".csv"
    if os.path.isfile(my_filename):
        with open(my_filename, 'r') as myfile:
            for curline in myfile:
                try:
                    pos_of_comma = curline.find(',')
                    if pos_of_comma > -1:
                        tweet_timestamp = int(curline[0:pos_of_comma])
                        tweet_text = unescape_str(curline[pos_of_comma + 1:])
                        tweet_list.append((tweet_timestamp, tweet_text))
                except ValueError:
                    pass
    return tweet_list

def diff_on_tweet_list(old_tweet_list, new_tweet_list):
    """returns new tweets from new_tweet_list which are not in old_tweet_list"""
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
    """writes a .csv file with the list of tweets"""
    with open(twitter_accountname + ".csv", 'w') as tweet_file:
        for cur_tweet in list_of_tweets:
            tweet_file.write(str(cur_tweet[0]) + "," + escape_str(cur_tweet[1]))
            tweet_file.write("\n")

def notify_about_new_tweets(twitter_accountname, list_of_new_tweets):
    """Uses system functionality to notify the user of new tweets"""
    perform_sleep_wait = True
    path_to_image = get_cwd() + "/apple-touch-icon.png"
    for cur_tweet in list_of_new_tweets:
        cur_delay = 11000 + int(len(cur_tweet[1]) / 40)
        tweet_timestr = datetime.fromtimestamp(cur_tweet[0]).strftime("%d. %b %H:%I:%S")
        notify_title = "@" + twitter_accountname + " " + tweet_timestr + ":"
        notify_text = cur_tweet[1] 
        try:
            call(["notify-send", "-c", "low", "-t", str(cur_delay - 500), "-i", path_to_image, notify_title, notify_text ])
            print("Notification: " + notify_title + " " + notify_text)
            if perform_sleep_wait:
                sleep(cur_delay / 1000)
        except KeyboardInterrupt:
            perform_sleep_wait = False

def get_cwd():
    return os.path.dirname(os.path.realpath(__file__))


def main(twitter_accountname):

    current_tweets = read_new_tweets(twitter_accountname)

    old_tweets = read_old_tweets(twitter_accountname)

    list_of_new_tweets = diff_on_tweet_list(old_tweets, current_tweets)

    write_tweets(twitter_accountname, old_tweets + list_of_new_tweets)

    if len(list_of_new_tweets) > 0:
        notify_about_new_tweets(twitter_accountname, list_of_new_tweets)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Twitter accountname required. None given. Aborting.")

