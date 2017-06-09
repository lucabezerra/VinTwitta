from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.utils import timezone
from rest_framework.test import APIRequestFactory

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
    def setUp(self):
        create_tweet()

    def test_tweet_is_stored(self):
        """ Creating a tweet in the DB should work as expected. """
        results = Tweet.objects.filter(provider_id=DEFAULT_TWEET_ID)
        self.assertIs(len(results), 1)

    def test_tweet_is_deleted(self):
        """ No tweets with the given ID should be found after deleting it. """
        Tweet.objects.get(provider_id=DEFAULT_TWEET_ID).delete()
        results = Tweet.objects.filter(provider_id=DEFAULT_TWEET_ID)
        self.assertIs(len(results), 0)


class SerializationTests(TestCase):
    def setUp(self):
        create_tweet()

    def test_tweet_gets_serialized(self):
        """ All the properties from a serialized tweet should be present. """
        tweet = Tweet.objects.get(provider_id=DEFAULT_TWEET_ID)
        serialized = TweetSerializer(tweet)
        self.assertIs(len(serialized.data), 5)


class APITests(TestCase):
    def setUp(self):
        # self.factory = APIRequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='lucabezerra_', email='luca@lol.com', password='pass_word')
        self.client = Client()
        self.client.force_login(self.user, backend='social_core.backends.twitter.TwitterOAuth')
        create_tweet()

    def test_user_tweets_are_fetched_and_stored(self):
        """ Given a Twitter handle, it should fetch the latest 200 tweets from its timeline and store them. """
        response = self.client.post('/tweets/process_add_handle/', {'userHandle': 'lucabezerra_'})
        # request = self.factory.post('/tweets/process_add_handle/', {'userHandle': 'lucabezerra_'})

        # from django.contrib.messages.storage.fallback import FallbackStorage
        # setattr(request, 'session', 'session')
        # messages = FallbackStorage(request)
        # setattr(request, '_messages', messages)
        #
        # request.user = self.user
        # response = add_handle(request)

        # There's a bug in unittest with Messages middleware:
        # https://stackoverflow.com/questions/11938164/why-dont-my-django-unittests-know-that-messagemiddleware-is-installed
        # TODO: Find a way to fix test so that we can fetch data from Twitter (which means using OAuth)
        self.assertEqual(response.status_code, 302)

    def test_list_tweets_by_username(self):
        """ Should list all tweets stored from a given username. """
        response = self.client.get('/tweets/filters/user/lucabezerra_/')
        data = response.json()

        self.assertIs(len(data), 1)
        self.assertEqual(data[0].get("owner"), "lucabezerra_")

    def test_list_tweets_by_unknown_username(self):
        """ Should try to find tweets from an unknown username and find none. """
        response = self.client.get('/tweets/filters/user/whatever/')
        data = response.json()

        self.assertIs(len(data), 0)

    def test_list_tweets_by_date(self):
        """ Should list all tweets stored that were tweeted past a given date. """
        date = datetime.now() - timedelta(days=5)
        response = self.client.get('/tweets/filters/date/{}/'.format(date))
        data = response.json()

        self.assertIs(len(data), 1)
        self.assertEqual(data[0].get("owner"), "lucabezerra_")

    def test_list_tweets_by_future_date(self):
        """ Should try to list tweets from a future date and find none. """
        date = datetime.now() + timedelta(days=1)
        response = self.client.get('/tweets/filters/date/{}/'.format(date))
        data = response.json()

        self.assertIs(len(data), 0)

    def test_list_tweets_by_text(self):
        """ Should list all tweets stored that contain a given text. """
        response = self.client.get('/tweets/filters/text/test/')
        data = response.json()

        self.assertIs(len(data), 1)
        self.assertEqual(data[0].get("owner"), "lucabezerra_")

    def test_list_tweets_by_wrong_text(self):
        """ Should try to list tweets that contain a given text and find none. """
        response = self.client.get('/tweets/filters/text/whatever/')
        data = response.json()

        self.assertIs(len(data), 0)

    def test_list_tweets_by_hashtag_with_hash_character(self):
        """ Should list all tweets stored that contain a given hashtag (including the hash character - #). """
        import urllib.parse
        hashtag = urllib.parse.quote_plus("#tweet")  # hash character gets encoded in real requests
        response = self.client.get('/tweets/filters/hashtag/{}/'.format(hashtag))
        data = response.json()

        self.assertIs(len(data), 1)
        self.assertEqual(data[0].get("owner"), "lucabezerra_")

    def test_list_tweets_by_wrong_hashtag_with_hash_character(self):
        """ Should try to list tweets stored that contain a given hashtag (including the hash character - #)
        and find none. """
        import urllib.parse
        hashtag = urllib.parse.quote_plus("#whatever")  # hash character gets encoded in real requests
        response = self.client.get('/tweets/filters/hashtag/{}/'.format(hashtag))
        data = response.json()

        self.assertIs(len(data), 0)

    def test_list_tweets_by_hashtag_without_hash_character(self):
        """ Should list all tweets stored that contain a given hashtag (NOT including the hash character - #). """
        # hashtags without the hash should also be searched for
        response = self.client.get('/tweets/filters/hashtag/tweet/')
        data = response.json()

        self.assertIs(len(data), 1)
        self.assertEqual(data[0].get("owner"), "lucabezerra_")

    def test_list_tweets_by_wrong_hashtag_without_hash_character(self):
        """ Should try to list tweets stored that contain a given hashtag (NOT including the hash character - #)
        and find none. """
        # hashtags without the hash should also be searched for
        response = self.client.get('/tweets/filters/hashtag/whatever/')
        data = response.json()

        self.assertIs(len(data), 0)

    def test_list_all_stored_hashtags(self):
        """ Should list all hashtags stored in the DB. """
        response = self.client.get('/tweets/list_hashtags/')
        data = response.json()

        self.assertIs(len(data), 2)
        self.assertEqual(data[0].get("name"), "#test")
        self.assertEqual(data[1].get("name"), "#tweet")
