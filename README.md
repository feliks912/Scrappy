Todo:
* Error handling:
  * Check something went wrong, please reload
  * Add username handling
* Save bot info to database
* load bots from db
  * balance the scrape load across them

* Bot replacement mechanism
  * Set remaining tweets to 0 when reaching something went wrong (after next day attempt)
  * Add scrape reset of the same day upon reaching the something went wrong, but avoid re-opening long tweets which are already in the database
  * Dynamic bot replacement, a replacement might have to be replaced, which might eat into reserved replacements for other bots.

Note:
* Enable data saving in accessibility options to prevent images and videos from loading
* Unfortunately this must be done manually for each account, but that's no big issue
* Even better since it's a Twitter's inbuilt feature


For prod:
* Basic error handling when elements are missing, timeouts, connection errors
* Resuming between instances
* Load balancing
* Automatic ban detection

Done:
* Twitter's limits:
  * Return viewed tweet count from scrape function
  * https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/faq
  * <i>The 24-hour period is based on a rolling clock, beginning at the time of the first request and monitored for the next 24 hours.</i>
    * Note the time of the first request, and it resets 24 hours later.
    * Must handle aborted requests and still note the number of tweets read
    * Save it to user file which we reset in a 24-hour period.