import re
from playwright.async_api import ElementHandle

import Tweet


async def get_tweet(card: ElementHandle, save_images=False, save_dir=None):
    """Extract data from tweet card"""
    image_links = []

    try:
        username_element = await card.query_selector('span')
        username = await username_element.inner_text() if username_element else None
    except Exception:
        return

    try:
        handle_element = await card.query_selector('span:has-text("@")')
        handle = await handle_element.inner_text() if handle_element else None
    except Exception:
        return

    try:
        postdate_element = await card.query_selector('time')
        postdate = await postdate_element.get_attribute('datetime') if postdate_element else None
    except Exception:
        return

    text = ""
    show_more = False

    try:
        text_element = await card.query_selector('div:nth-of-type(2) > div:nth-of-type(2) > div:nth-of-type(2)')
        text = await text_element.inner_text() if text_element else ""
    except Exception:
        return

    is_reply = False

    # TODO: Implement replies later. For now, just ignore them
    # if len(text) >= 14 and text[:14] == 'Replying to \n@':
    #     is_reply = True
    #     try:
    #         text_element = await card.query_selector('div:nth-of-type(2) > div:nth-of-type(2) > div:nth-of-type(3)')
    #         text = await text_element.inner_text() if text_element else ""
    #     except Exception:
    #         return

    if len(text) >= 9 and text[-9:] == 'Show more':
        show_more = True

    reply_cnt, retweet_cnt, like_cnt, reach = 0, 0, 0, 0

    try:
        reply_element = await card.query_selector('div[data-testid="reply"]')
        reply_cnt = await reply_element.inner_text() if reply_element else 0

        if reply_cnt[-1] == 'K':
            reply_cnt = int(float(reply_cnt[:-1])*1000)
        elif reply_cnt[-1] == 'M':
            reply_cnt = int(float(reply_cnt[:-1]) * 10e6)
        else:
            reply_cnt = int(reply_cnt)

    except Exception:
        pass

    try:
        retweet_element = await card.query_selector('div[data-testid="retweet"]')
        retweet_cnt = await retweet_element.inner_text() if retweet_element else 0

        if retweet_cnt[-1] == 'K':
            retweet_cnt = int(float(retweet_cnt[:-1])*1000)
        elif retweet_cnt[-1] == 'M':
            retweet_cnt = int(float(retweet_cnt[:-1]) * 10e6)
        else:
            retweet_cnt = int(retweet_cnt)

    except Exception:
        pass

    try:
        like_element = await card.query_selector('div[data-testid="like"]')
        if not like_element:
            like_element = await card.query_selector('div[data-testid="unlike"]')

        like_cnt = await like_element.inner_text() if like_element else 0
        if like_cnt[-1] == 'K':
            like_cnt = int(float(like_cnt[:-1])*1000)
        elif like_cnt[-1] == 'M':
            like_cnt = int(float(like_cnt[:-1]) * 10e6)
        else:
            like_cnt = int(like_cnt)

    except Exception:
        pass

    try:
        reach_element = await card.query_selector('div[aria-label*="views"] > div:nth-of-type(4)')
        reach = await reach_element.inner_text() if reach_element else 0

        if reach[-1] == 'K':
            reach = int(float(reach[:-1])*1000)
        elif reach[-1] == 'M':
            reach = int(float(reach[:-1]) * 10e6)
        else:
            reach = int(reach)
    except Exception:
        pass

    try:
        elements = await card.query_selector_all('div:nth-of-type(2) > div:nth-of-type(2) img[src*="https://pbs.twimg.com/"]')
        image_links = [await element.get_attribute('src') for element in elements]
    except Exception:
        image_links = []

    # Get a string of all emojis contained in the tweet
    emoji_list = []
    try:
        emoji_tags = await card.query_selector_all('img[src*="emoji"]')
        for tag in emoji_tags:
            try:
                filename = await tag.get_attribute('src')
                emoji = chr(int(re.search(r'svg\/([a-z0-9]+)\.svg', filename).group(1), base=16))
                emoji_list.append(emoji)
            except AttributeError:
                continue
    except Exception:
        pass

    # Tweet URL
    try:
        element = await card.query_selector('a[href*="/status/"]')
        tweet_url = await element.get_attribute('href') if element else None
        if tweet_url is not None:
            tweet_url = "https://twitter.com" + tweet_url
    except Exception:
        return

    tweet = Tweet.Tweet(username, handle, postdate, text, is_reply, emoji_list, reach, reply_cnt, retweet_cnt, like_cnt,
                        image_links, tweet_url, show_more)

    return tweet
