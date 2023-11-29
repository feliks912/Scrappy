import scrappy_init
import scrappy_search
import scrappy_scrape
import time

# Start chromium, load extensions, open Twitter, load cookies, refresh
driver = scrappy_init.init()

results = scrappy_search.search(driver, "thejacobmars", "2023-11-18", "2023-11-21", no_replies=True)

tweets = scrappy_scrape.scrape_search(results, 20)

input("hellO!")