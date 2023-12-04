import time

import scrappy_init
import scrappy_search
from pathlib import Path
from playwright.sync_api import sync_playwright
import json


def main():
    datas = [
        ("feliks912", 20, "2023-11-10", "2023-11-21", Path('cookies_RadRefraction38.json')),
        ("thejacobmars", 20, "2023-11-10", "2023-11-21", Path('cookies_StarStones24.json')),
    ]

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False
        )

        user_data = Path('cookies_feliks912.json')

        context = scrappy_init.init_context(browser, user_data)

        update_cookies(context.cookies("https://twitter.com"), user_data)

        time.sleep(1000)

        context.close()

    search_url = scrappy_search.search("feliks912", "2023-11-10", "2023-11-21", no_replies=True)


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

    # for i in range(0, len(datas)):
    #     driver = scrappy_init.init(user_data=datas[i][4])
    #     search_url = scrappy_search.search(datas[i][0], datas[i][2], datas[i][3], no_replies=True)
    #     print(f"Search URL obtained: {search_url}")
    #
    #     tweets = scrappy_scrape.scrape_search(search_url, 20)
    #     print(f"Scraped {len(tweets)} tweets")
    #
    #     #mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
    #     #mongo_db = mongo_client["tweets"]
    #     #user_tweets = mongo_db[datas[i][0]]
    #     #user_tweets.insert_many([tweet.to_dict() for tweet in tweets])
    #     #print("Tweets inserted into MongoDB")


if __name__ == "__main__":
    main()
