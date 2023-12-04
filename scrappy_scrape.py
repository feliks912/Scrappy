from playwright.async_api import BrowserContext, TimeoutError
import scrappy_get  # Assuming this is a custom module for handling tweet data


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

    while True:
        tweets_count = len(tweets)
        try:
            await page.wait_for_selector('article[data-testid="tweet"]', timeout=5000)
        except TimeoutError:
            break  # No tweets to load or load error

        page_cards = await page.query_selector_all('article[data-testid="tweet"]')

        break_loop = False

        for card in page_cards:
            tweet = await scrappy_get.get_tweet(card)  # Adjust get_tweet to be async and compatible with Playwright
            if tweet is not None:
                if tweet.show_more:
                    read_more_tweets.add(tweet)
                else:
                    tweets.add(tweet)

            if 0 < limit <= len(tweets) + len(read_more_tweets):
                break_loop = True
                break

        if break_loop:
            break

        if len(tweets) == tweets_count:
            break

        await page.keyboard.press('End')
        try:
            await page.locator(progress_bar_selector).wait_for(timeout=5000, state="hidden")
        except TimeoutError:
            break  # No more tweets to load or load error

        await page.wait_for_timeout(100)  # Give it a little bit of time to load more tweets

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
            try:
                await tweet_page.wait_for_selector('div[data-testid="tweetText"]', timeout=2500)
            except TimeoutError:
                continue

            text = await tweet_page.inner_text('div[data-testid="tweetText"]')
            tweet.text = text
            tweets.add(tweet)
            await tweet_page.close()

    return list(tweets)
