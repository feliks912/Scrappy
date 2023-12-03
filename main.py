import threading
import scrappy_init
import scrappy_search
import scrappy_scrape
import pymongo
from pathlib import Path
from time import sleep


class ScrapeThread(threading.Thread):
    def __init__(self, username, limit, begin, end, user_file):
        threading.Thread.__init__(self)
        self.username = username
        self.limit = limit
        self.begin = begin
        self.end = end
        self.user_file = user_file

    def run(self):
        try:
            print(f"Starting scraper for {self.username}")
            driver = scrappy_init.init(self.user_file)
            print("WebDriver initialized")

            search_url = scrappy_search.search(driver, self.username, self.begin, self.end, no_replies=True)
            print(f"Search URL obtained: {search_url}")

            tweets = scrappy_scrape.scrape_search(search_url, self.limit)
            print(f"Scraped {len(tweets)} tweets")

            mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
            mongo_db = mongo_client["tweets"]
            user_tweets = mongo_db[self.username]
            user_tweets.insert_many([tweet.to_dict() for tweet in tweets])
            print("Tweets inserted into MongoDB")

            driver.close()

        except Exception as e:
            print(f"Error in run_scraper for user {self.username}: {e}")
        finally:
            print("WebDriver closed")


def main():
    scrapers = [
       ("feliks912", 20, "2023-11-10", "2023-11-21", Path('cookies_RadRefraction38.json')),
       ("thejacobmars", 20, "2023-11-10", "2023-11-21", Path('cookies_StarStones24.json')),
    ]

    threads = []
    for scraper in scrapers:
        print(f"Creating thread with arguments: {scraper}")
        t = ScrapeThread(*scraper)
        print("Starting thread")
        t.start()
        sleep(2)
        print("Appending thread to list")
        threads.append(t)

    for t in threads:
        print("Joining thread")
        t.join()


if __name__ == "__main__":
    main()

print("Done!")
