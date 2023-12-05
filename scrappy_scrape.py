from playwright.async_api import BrowserContext, TimeoutError
import scrappy_get  # Assuming this is a custom module for handling tweet data
import asyncio


async def scrape_search(advanced_url: str, context: BrowserContext, limit=-1, batch_size=5):
    """
    Gets the Twitter advanced search timeline and scrapes limit tweets off of it.

    Tweets with 'Read more' can't have their text fetched on the timeline, so upon scraping all tweets the script opens those tweets separately 5 at a time in separate tabs and overwrites the text.

    :param batch_size:
    :param context:
    :param advanced_url:
    :param limit: How many tweets to scrape
    :return: a list of scraped tweets
    """

    tweets = set()
    read_more_tweets = set()

    progress_bar_selector = 'div[data-testid="primaryColumn"] div[data-testid="cellInnerDiv"] div[role="progressbar"]'

    page = context.pages[0] # Assuming the first page is the search page

    await page.goto(advanced_url)

    await page.locator('article[data-testid="tweet"]').nth(0).is_visible()

    page_up_attempted = False

    while True:
        tweets_count = len(tweets) + len(read_more_tweets)

        page_cards = await page.query_selector_all('article[data-testid="tweet"]')

        break_loop = False

        for card in page_cards:
            tweet = await scrappy_get.get_tweet(card)  # Adjust get_tweet to be async and compatible with Playwright
            if tweet is not None:
                if tweet.show_more:
                    print("got tweet " + tweet.tweet_url)
                    read_more_tweets.add(tweet)
                else:
                    tweets.add(tweet)

            if 0 < limit <= len(tweets) + len(read_more_tweets):
                print("Found all tweets")
                break_loop = True
                break

        if break_loop:
            break

        if len(tweets) + len(read_more_tweets) == tweets_count:
            if page_up_attempted:
                print("Same number of tweets after scroll")
                break

            await page.keyboard.press('PageUp')
            await page.keyboard.press('PageUp')
            await page.wait_for_timeout(500)
            page_up_attempted = True
        elif page_up_attempted:
            page_up_attempted = False

        await page.keyboard.press('End')

        loading_selectors = page.locator(progress_bar_selector)

        # Get the count of elements that match the locator
        element_count = await loading_selectors.count()

        # Create a list of tasks for each element based on its index
        tasks = [loading_selectors.nth(i).is_hidden() for i in range(element_count)]

        # Wait for all tasks (each element to be hidden) to complete
        await asyncio.gather(*tasks)

        await page.wait_for_timeout(500)  # Give it a little bit of time to load more tweets

    read_more_tweets = list(read_more_tweets)

    for i in range(0, len(read_more_tweets), batch_size):
        current_batch = read_more_tweets[i:i + batch_size]
        pages = []

        # Open a batch of tabs
        for tweet in current_batch:
            if tweet.tweet_url is not None:
                tweet_page = await page.context.new_page()
                await tweet_page.goto(tweet.tweet_url)
                pages.append((tweet_page, tweet))

        # Process each tab in the batch
        for tweet_page, tweet in pages:
            tweet_text_path = 'div[data-testid="tweetText"]'

            await tweet_page.locator(tweet_text_path).nth(0).is_visible()

            text = await tweet_page.inner_text(tweet_text_path)

            tweet.text = text
            print("got long tweet " + tweet.tweet_url)
            tweets.add(tweet)

            await tweet_page.close()

    return list(tweets)
