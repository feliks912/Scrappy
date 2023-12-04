
def search(username: str, since: str, until: str = None, no_replies: bool = False):
    return log_search_page(from_account=username, since=since, until_local=until, display_type='Latest', no_replies=no_replies)


def log_search_page(since, until_local, lang=None, display_type=None, words=None, to_account=None, from_account=None,
                    mention_account=None,
                    hashtag=None, filter_replies=None, proximity=None,
                    geocode=None, minreplies=None, minlikes=None, minretweets=None, no_replies=None):
    """ Search for this query between since and until_local"""
    # format the <from_account>, <to_account> and <hash_tags>
    from_account = "(from%3A" + from_account + ")%20" if from_account is not None else ""
    to_account = "(to%3A" + to_account + ")%20" if to_account is not None else ""
    mention_account = "(%40" + mention_account + ")%20" if mention_account is not None else ""
    hash_tags = "(%23" + hashtag + ")%20" if hashtag is not None else ""

    if words is not None:
        if len(words) == 1:
            words = "(" + str(''.join(words)) + ")%20"
        else:
            words = "(" + str('%20OR%20'.join(words)) + ")%20"
    else:
        words = ""

    if lang is not None:
        lang = 'lang%3A' + lang
    else:
        lang = ""

    until_local = "until%3A" + until_local + "%20"
    since = "since%3A" + since + "%20"

    if display_type == "Latest" or display_type == "latest":
        display_type = "&f=live"
    elif display_type == "Image" or display_type == "image":
        display_type = "&f=image"
    else:
        display_type = ""

    # filter replies
    if filter_replies == True:
        filter_replies = "%20-filter%3Areplies"
    else:
        filter_replies = ""
    # geo
    if geocode is not None:
        geocode = "%20geocode%3A" + geocode
    else:
        geocode = ""
    # min number of replies
    if minreplies is not None:
        minreplies = "%20min_replies%3A" + str(minreplies)
    else:
        minreplies = ""
    # min number of likes
    if minlikes is not None:
        minlikes = "%20min_faves%3A" + str(minlikes)
    else:
        minlikes = ""
    # min number of retweets
    if minretweets is not None:
        minretweets = "%20min_retweets%3A" + str(minretweets)
    else:
        minretweets = ""

    # proximity
    if proximity == True:
        proximity = "&lf=on"  # at the end
    else:
        proximity = ""

    if no_replies == True:
        no_replies = "-filter%3Areplies%20"
    else:
        no_replies = ""

    path = 'https://twitter.com/search?q=' + words + from_account + to_account + mention_account + hash_tags + until_local + no_replies + since + lang + filter_replies + geocode + minreplies + minlikes + minretweets + '&src=typed_query' + display_type + proximity

    return path
