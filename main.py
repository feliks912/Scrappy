import time

import pymongo

import scrappy_init
import scrappy_scrape
import scrappy_search
from pathlib import Path
from playwright.async_api import async_playwright
import json

import asyncio


async def main():
    datas = [
        ("feliks912", 20, "2023-11-10", "2023-11-21", Path('cookies_RadRefraction38.json')),
        ("thejacobmars", 20, "2023-11-10", "2023-11-21", Path('cookies_StarStones24.json')),
    ]

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=False
        )

        username = "thejacobmars"

        user_data = Path('cookies_StarStones24.json')

        context = await scrappy_init.init_context(browser, user_data)

        search_url = scrappy_search.search(username, "2022-10-10", "2023-11-21", no_replies=True)

        tweets = await scrappy_scrape.scrape_search(search_url, context, 50)

        update_cookies(await context.cookies("https://twitter.com"), user_data)

        dump_to_database(username, tweets)

        await context.close()


def update_cookies(cookies: dict, user_data: Path):
    if cookies is not None:
        if user_data.exists():
            with user_data.open('r') as file:
                data = json.load(file)
        else:
            return

        data['cookies'] = cookies

        # write cookies to file
        with user_data.open('w') as file:
            json.dump(data, file)


def dump_to_database(username: str, tweets: set):
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
    mongo_db = mongo_client["tweets"]
    user_tweets = mongo_db[username]
    user_tweets.insert_many([tweet.to_dict() for tweet in tweets])
    print("Tweets inserted into MongoDB")

if __name__ == "__main__":
    asyncio.run(main())
    print("Done!")
