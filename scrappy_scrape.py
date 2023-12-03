from altair import TimeUnit
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import scrappy_get
import math
import Tweet


def scrape_search(driver: webdriver, limit: int = -1):
    """
    Gets the Twitter advance search timeline and scrapes limit tweets off of it.

    Tweets with 'Read more' can't have their text fetched on the timeline, so upon scraping all tweets the script opens those tweets separately 5 at a time in separate tabs and overwrites the text.

    :param driver: chromedriver/geckodriver instance
    :param limit: How many tweets to scrape
    :return: a set of scraped tweets
    """

    tweets = set()

    progress_bar_xpath = "//div[@data-testid='primaryColumn']//div[@data-testid='cellInnerDiv']//div[@role='progressbar']"

    # Wait until the loading circle is present
    WebDriverWait(driver, timeout=10, poll_frequency=0.25).until(
        EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]'))
    )

    while True:

        tweets_count = len(tweets)

        page_cards = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')  # changed div by article

        for card in page_cards:
            tweet = scrappy_get.get_tweet(card)  # Assuming this function returns a Tweet object or similar

            if tweet is not None:
                tweets.add(tweet)

            if 0 < limit <= len(tweets):
                break

        if len(tweets) == tweets_count:
            break

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

        # Wait until the loading circle is present
        WebDriverWait(driver, timeout=10, poll_frequency=0.25).until_not(
            EC.presence_of_element_located((By.XPATH, progress_bar_xpath))
        )

        driver.implicitly_wait(0.1)

    read_more_tweets = [tweet for tweet in tweets if tweet.show_more]

    tweets = [tweet for tweet in tweets if not tweet.show_more]

    while len(read_more_tweets) > 0:

        counter = min(5, len(read_more_tweets))

        for i in range(0, counter):
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(read_more_tweets[i].tweet_url)

        for i in range(0, counter):
            driver.switch_to.window(driver.window_handles[1])

            tweet_content_xpath = "//div[@aria-label='Timeline: Conversation']//div[@data-testid='cellInnerDiv']//div[@data-testid='tweetText']"
            WebDriverWait(driver, timeout=10, poll_frequency=0.25).until(
                EC.presence_of_element_located((By.XPATH, tweet_content_xpath))
            )

            # Get the text of the tweet
            text = driver.find_element(By.XPATH, tweet_content_xpath).text

            read_more_tweets[0].text = text

            tweets.append(read_more_tweets[0])

            read_more_tweets.pop(0)

            # Close the tab and switch back to the main search results tab
            driver.close()

        driver.switch_to.window(driver.window_handles[-1])

    #driver.close()

    return list(tweets)
