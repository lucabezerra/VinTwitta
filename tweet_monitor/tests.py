from django.test import TestCase
from django.utils import timezone

from .models import Tweet, Hashtag
from .serializers import TweetSerializer, HashtagSerializer


DEFAULT_TWEET_ID = "1234567890"


def create_tweet():
    tweet = Tweet()
    tweet.provider_id = DEFAULT_TWEET_ID
    tweet.owner = "lucabezerra_"
    tweet.text = "This is a test tweet. #test #tweet"
    tweet.creation_date = timezone.now()
    tweet.save()
    tweet.extract_hashtags()


class TweetsDatabaseTests(TestCase):
    def test_tweet_is_stored(self):
        """ Creating a tweet in the DB should work as expected. """
        create_tweet()

        results = Tweet.objects.filter(provider_id=DEFAULT_TWEET_ID)
        self.assertIs(len(results), 1)

    def test_tweet_is_deleted(self):
        """ No tweets with the given ID should be found after deleting it. """
        create_tweet()

        Tweet.objects.get(provider_id=DEFAULT_TWEET_ID).delete()
        results = Tweet.objects.filter(provider_id=DEFAULT_TWEET_ID)
        self.assertIs(len(results), 0)


class SerializationTests(TestCase):
    def test_tweet_gets_serialized(self):
        """ All the properties from a serialized tweet should be present. """
        create_tweet()

        tweet = Tweet.objects.get(provider_id=DEFAULT_TWEET_ID)
        serialized = TweetSerializer(tweet)
        self.assertIs(len(serialized.data), 5)

