from datetime import datetime, timedelta
import time

import pymongo

import scrappy_init
import scrappy_scrape
import scrappy_search
from pathlib import Path
from playwright.async_api import async_playwright, Browser
import json

import asyncio

daily_view_limit = 1000  # Tweets per day

"""
*** Input: dict
    account handle
    number of tweets per account
    number of tweets to scrape per account
    weights per account?
    
    Example:
    {
        "bots": [{
            "id": 0,
            "tweets_remaining": 142
        },
        {
            "id": 1,
            "tweets_remaining": 142
        },
        {
            "id": 2,
            "tweets_remaining": 142
        }],
        "accounts": 
        [{
            "user": "@feliks912",
            "tweets": 200,
            "tweets_to_scrape": 100,
            "weight": 0.3
        },
        {
            "user": "@thejacobmars",
            "tweets": 5900,
            "tweets_to_scrape": 3000,
            "weight": 0.1
        },
        {
            "user": "@elonmusk",
            "tweets": 39000,
            "tweets_to_scrape": 10000,
            "weight": 0.4
        },
        {
            "user": "@thedankoe",
            "tweets": 15300,
            "tweets_to_scrape": 10000,
            "weight": 0.2
        }]
    }


*** Output:
    a struct of handles and tweet counts per bot
    
    Example:
    [{
        "user": "@feliks912",
        "bots": {
            "id": 19,
            "start_date": [iso_datetime],
            "jump_days": 0
        }    
    },
    {
        "user": "@thejacobmars",
        "bots": [{
            "id": 1,
            "start_date": [iso_datetime],
            "jump_days": 2
        },
        {
            "id": 5,
            "start_date": [iso_datetime],
            "jump_days": 2
        },
        {
            "id": 14,
            "start_date": [iso_datetime],
            "jump_days": 2
        }]    
    }]
"""


async def main():
    global daily_view_limit
    datas = [
        ("feliks912", 20, "2023-11-10", "2023-11-21", Path('cookies_RadRefraction38.json')),
        ("thejacobmars", 20, "2023-11-10", "2023-11-21", Path('cookies_StarStones24.json')),
    ]

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=False
        )

        await run_scraper("feliks912", Path('cookies_feliks912.json'), 100, browser)


async def run_scraper(username: str, user_data: Path, limit: int, browser: Browser):

    context = await scrappy_init.init_context(browser, user_data)

    search_url = scrappy_search.search(
        username,
        "2021-12-20",
        "2023-01-20",
        no_replies=True
    )

    first_request_timestamp, remaining_views = read_user_data(user_data)

    tweets, remaining_views, return_code = await scrappy_scrape.scrape_search(search_url, context, remaining_views, 20)

    update_user_data(await context.cookies("https://twitter.com"), first_request_timestamp, remaining_views, user_data)

    tweet_to_database(username, tweets)

    await context.close()

def read_user_data(user_data: Path):
    with user_data.open('r') as file:
        userdata = json.load(file)

        first_request_iso = userdata['first_request_timestamp']

        if first_request_iso == "":
            first_request_timestamp = datetime.now()
        else:
            first_request_timestamp = datetime.fromisoformat(first_request_iso)

        if datetime.now() - first_request_timestamp >= timedelta(hours=24):
            remaining_views = daily_view_limit
            first_request_timestamp = datetime.now()
            print("User limit reset, 24 hours have passed")

        else:
            remaining_views = userdata['remaining_views']

            if remaining_views <= 0:
                print("User has no more remaining views, stopping.")
                exit(1)

        return first_request_timestamp, remaining_views


def update_user_data(cookies: dict, first_request_timestamp: datetime, remaining_views: int, user_data: Path):
    if cookies is not None:
        if user_data.exists():
            with user_data.open('r') as file:
                data = json.load(file)
        else:
            return

        data['cookies'] = cookies
        data['remaining_views'] = remaining_views
        data['first_request_timestamp'] = first_request_timestamp.isoformat()

        # write cookies to file
        with user_data.open('w') as file:
            json.dump(data, file)


def user_to_database(identifier: str, data: json):
    pass

def tweet_to_database(username: str, tweets: set):
    if tweets is not None:
        mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
        mongo_db = mongo_client["tweets"]
        user_tweets = mongo_db[username]
        user_tweets.insert_many([tweet.to_dict() for tweet in tweets])
        print("Tweets inserted into MongoDB")


if __name__ == "__main__":
    asyncio.run(main())
    print("Done!")
