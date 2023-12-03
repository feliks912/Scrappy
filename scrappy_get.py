import Tweet
import re
from selenium.webdriver.common.by import By


def get_tweet(card, save_images=False, save_dir=None):
    """Extract data from tweet card"""
    image_links = []

    try:
        username = card.find_element(By.XPATH, './/span').text
    except:
        return

    try:
        handle = card.find_element(By.XPATH, './/span[contains(text(), "@")]').text
    except:
        return

    try:
        postdate = card.find_element(By.XPATH, './/time').get_attribute('datetime')
    except:
        return

    text = ""
    show_more = False

    try:
        text = card.find_element(By.XPATH, './/div[2]/div[2]/div[2]').text
    except:
        return

    is_reply = False

    if len(text) >= 14 and text[:14] == 'Replying to \n@':
        is_reply = True
        try:
            text = card.find_element(By.XPATH, './/div[2]/div[2]/div[3]').text
        except:
            return

    if len(text) >= 9 and text[-9:] == 'Show more':
        show_more = True

    try:
        reply_cnt = int(card.find_element(By.XPATH, './/div[@data-testid="reply"]').text)
    except:
        reply_cnt = 0

    try:
        retweet_cnt = int(card.find_element(By.XPATH, './/div[@data-testid="retweet"]').text)
    except:
        retweet_cnt = 0

    try:
        like_cnt = int(card.find_element(By.XPATH, './/div[@data-testid="like"]').text)
    except:
        like_cnt = 0

    try:
        # Dirty with div[4] but no other selector is given for the div. It works.
        reach = int(card.find_element(By.XPATH, ".//div[contains(@aria-label, 'views')]/div[4]").text)
    except:
        reach = 0

    try:
        elements = card.find_elements(By.XPATH, './/div[2]/div[2]//img[contains(@src, "https://pbs.twimg.com/")]')
        for element in elements:
            image_links.append(element.get_attribute('src'))
    except:
        image_links = []

    # if save_images == True:
    #	for image_url in image_links:
    #		save_image(image_url, image_url, save_dir)
    # handle promoted tweets

    # get a string of all emojis contained in the tweet
    try:
        emoji_tags = card.find_elements(By.XPATH, './/img[contains(@src, "emoji")]')
    except:
        return
    emoji_list = []
    for tag in emoji_tags:
        try:
            filename = tag.get_attribute('src')
            emoji = chr(int(re.search(r'svg\/([a-z0-9]+)\.svg', filename).group(1), base=16))
        except AttributeError:
            continue
        if emoji:
            emoji_list.append(emoji)

    # tweet url
    try:
        element = card.find_element(By.XPATH, './/a[contains(@href, "/status/")]')
        tweet_url = element.get_attribute('href')
    except:
        return

    tweet = Tweet.Tweet(username, handle, postdate, text, is_reply, emoji_list, reach, reply_cnt, retweet_cnt, like_cnt,
                        image_links, tweet_url, show_more)

    return tweet
