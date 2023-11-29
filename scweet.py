import csv
import os
import datetime
import argparse
from time import sleep
import random
import pandas as pd

from utils import init_driver, get_last_date_from_csv, log_search_page, keep_scroling, dowload_images


def scrape(account:str=None, since:str=None, until:str=None):

        # log search page for a specific <interval> of time and keep scrolling unltil scrolling stops or reach the <until>
    while until_local <= datetime.datetime.strptime(until, '%Y-%m-%d'):
        # number of scrolls
        scroll = 0
        # convert <since> and <until_local> to str
        if type(since) != str:
            since = datetime.datetime.strftime(since, '%Y-%m-%d')
        if type(until_local) != str:
            until_local = datetime.datetime.strftime(until_local, '%Y-%m-%d')
        # log search page between <since> and <until_local>
        path = log_search_page(driver=driver, words=words, since=since,
                               until_local=until_local, to_account=to_account,
                               from_account=from_account, mention_account=mention_account, hashtag=hashtag,
                               lang=lang,
                               display_type=display_type, filter_replies=filter_replies, proximity=proximity,
                               geocode=geocode, minreplies=minreplies, minlikes=minlikes, minretweets=minretweets)
        # number of logged pages (refresh each <interval>)
        refresh += 1
        # number of days crossed
        # days_passed = refresh * interval
        # last position of the page : the purpose for this is to know if we reached the end of the page or not so
        # that we refresh for another <since> and <until_local>
        last_position = driver.execute_script("return window.pageYOffset;")
        # should we keep scrolling ?
        scrolling = True
        print("looking for tweets between " + str(since) + " and " + str(until_local) + " ...")
        print(" path : {}".format(path))
        # number of tweets parsed
        tweet_parsed = 0
        # sleep
        sleep(random.uniform(0.5, 1.5))
        # start scrolling and get tweets
        driver, data, writer, tweet_ids, scrolling, tweet_parsed, scroll, last_position = \
            keep_scroling(driver, data, writer, tweet_ids, scrolling, tweet_parsed, limit, scroll, last_position)

        # keep updating <start date> and <end date> for every search
        if type(since) == str:
            since = datetime.datetime.strptime(since, '%Y-%m-%d') + datetime.timedelta(days=interval)
        else:
            since = since + datetime.timedelta(days=interval)
        if type(since) != str:
            until_local = datetime.datetime.strptime(until_local, '%Y-%m-%d') + datetime.timedelta(days=interval)
        else:
            until_local = until_local + datetime.timedelta(days=interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape tweets.')

    parser.add_argument('--words', type=str,
                        help='Queries. they should be devided by "//" : Cat//Dog.', default=None)
    parser.add_argument('--from_account', type=str,
                        help='Tweets from this account (example : @Tesla).', default=None)
    parser.add_argument('--to_account', type=str,
                        help='Tweets replyed to this account (example : @Tesla).', default=None)
    parser.add_argument('--mention_account', type=str,
                        help='Tweets mention a account (example : @Tesla).', default=None)
    parser.add_argument('--hashtag', type=str,
                        help='Hashtag', default=None)
    parser.add_argument('--until', type=str,
                        help='Max date for search query. example : %%Y-%%m-%%d.', required=True)
    parser.add_argument('--since', type=str,
                        help='Start date for search query. example : %%Y-%%m-%%d.', required=True)
    parser.add_argument('--interval', type=int,
                        help='Interval days between each start date and end date for search queries. example : 5.',
                        default=1)
    parser.add_argument('--lang', type=str,
                        help='Tweets language. example : "en" for english and "fr" for french.', default=None)
    parser.add_argument('--headless', type=bool,
                        help='Headless webdrives or not. True or False', default=False)
    parser.add_argument('--limit', type=int,
                        help='Limit tweets per <interval>', default=float("inf"))
    parser.add_argument('--display_type', type=str,
                        help='Display type of twitter page : Latest or Top', default="Top")
    parser.add_argument('--resume', type=bool,
                        help='Resume the last scraping. specify the csv file path.', default=False)
    parser.add_argument('--proxy', type=str,
                        help='Proxy server', default=None)
    parser.add_argument('--proximity', type=bool,
                        help='Proximity', default=False)
    parser.add_argument('--geocode', type=str,
                        help='Geographical location coordinates to center the search, radius. No compatible with proximity',
                        default=None)
    parser.add_argument('--minreplies', type=int,
                        help='Min. number of replies to the tweet', default=None)
    parser.add_argument('--minlikes', type=int,
                        help='Min. number of likes to the tweet', default=None)
    parser.add_argument('--minretweets', type=int,
                        help='Min. number of retweets to the tweet', default=None)

    args = parser.parse_args()

    words = args.words
    until = args.until
    since = args.since
    interval = args.interval
    lang = args.lang
    headless = args.headless
    limit = args.limit
    display_type = args.display_type
    from_account = args.from_account
    to_account = args.to_account
    mention_account = args.mention_account
    hashtag = args.hashtag
    resume = args.resume
    proxy = args.proxy
    proximity = args.proximity
    geocode = args.geocode
    minreplies = args.minreplies
    minlikes = args.minlikes
    minretweets = args.minlikes

    data = scrape(since=since, until=until, words=words, to_account=to_account, from_account=from_account,
                  mention_account=mention_account,
                  hashtag=hashtag, interval=interval, lang=lang, headless=headless, limit=limit,
                  display_type=display_type, resume=resume, proxy=proxy, filter_replies=False, proximity=proximity,
                  geocode=geocode, minreplies=minreplies, minlikes=minlikes, minretweets=minretweets)
