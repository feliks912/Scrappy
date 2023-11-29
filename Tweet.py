from typing import List, Set, Optional


class Tweet:
    urls = []

    view_limit = 10000
    total_viewed_tweets = 0

    @classmethod
    def increase_and_check_view_limit(cls):
        cls.total_viewed_tweets += 1
        if cls.total_viewed_tweets >= cls.view_limit:
            return True
        return False

    collected_limit = 50
    total_collected_tweets = 0

    @classmethod
    def increase_and_check_collection_limit(cls):
        cls.total_collected_tweets += 1
        if cls.total_collected_tweets >= cls.collected_limit:
            return True
        return False

    """
    Represents a Tweet object with various attributes.

    Attributes:
        username (str): The username of the tweet author.
        handle (str): The Twitter handle of the tweet author.
        postdate (str): The date when the tweet was posted.
        text (str): The content of the tweet.
        embedded (bool): Indicates whether the tweet contains embedded media.
        emojis (list): A list of emojis used in the tweet.
        reach (int): How many people saw the tweet.
        reply_cnt (int): The number of replies to the tweet.
        retweet_cnt (int): The number of retweets of the tweet.
        like_cnt (int): The number of likes (favorites) on the tweet.
        image_links (list): A list of links to images included in the tweet.
        tweet_url (str): The URL of the tweet on Twitter.
        replies (list): A list of reply Tweet objects to this tweet.
    """

    def __init__(self,
                 username: str,
                 handle: str,
                 postdate: str,
                 text: str,
                 is_reply: bool,
                 emojis: List[str],
                 reach: int,
                 reply_cnt: int,
                 retweet_cnt: int,
                 like_cnt: int,
                 image_links: List[str],
                 tweet_url: str,
                 show_more: bool,
                 replies: Optional[Set['Tweet']] = None,
                 replied_to: Optional['Tweet'] = None):
        self.username = username
        self.handle = handle
        self.postdate = postdate
        self.text = text
        self.is_reply = is_reply
        self.reach = reach
        self.emojis = emojis
        self.reply_cnt = reply_cnt
        self.retweet_cnt = retweet_cnt
        self.like_cnt = like_cnt
        self.image_links = image_links
        self.tweet_url = tweet_url
        self.show_more = show_more
        self.replies = replies if replies is not None else set()  # Initialize tweet_url to None
        self.replied_to = replied_to

    def add_reply(self, reply):
        self.replies.add(reply)

    def to_dict(self):
        """
        Convert the Tweet object to a dictionary.

        Returns:
            dict: A dictionary representation of the Tweet object.
        """
        return {
            'username': self.username,
            'handle': self.handle,
            'postdate': self.postdate,
            'text': self.text,
            'is_reply': self.is_reply,
            'emojis': self.emojis,
            'reach': self.reach,
            'reply_cnt': self.reply_cnt,
            'retweet_cnt': self.retweet_cnt,
            'like_cnt': self.like_cnt,
            'image_links': self.image_links,
            'tweet_url': self.tweet_url,
            'show_more': self.show_more,
            'replies': [reply.to_dict() for reply in self.replies]
        }

    def __hash__(self):
        # Create a unique string identifier for the tweet
        unique_identifier = f"{self.postdate}_{self.handle}"
        # Return the hash of this unique identifier
        return hash(unique_identifier)

    def __eq__(self, other):
        if isinstance(other, Tweet):
            return self.postdate == other.postdate and self.handle == other.handle
        return False

    def __str__(self):
        """
        Return a string representation of the Tweet object.

        Returns:
            str: A string representation of the Tweet.
        """
        return f"Tweet by {self.username} (@{self.handle}) on {self.postdate}:\n{self.text}"
