from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from rest_framework import generics
from social_django.models import UserSocialAuth
import tweepy
from tweepy import TweepError

from .models import Tweet, Hashtag
from .serializers import TweetSerializer


# ########### Retrieval Endpoints ########### #


class TweetsView(generics.ListAPIView):
    """ Returns a list of all tweets. """
    model = Tweet
    serializer_class = TweetSerializer

    def get_queryset(self):
        return Tweet.objects.all()


class UserTweetsView(generics.ListAPIView):
    """ Returns a list of all tweets from a specific user. """
    model = Tweet
    serializer_class = TweetSerializer

    def get_queryset(self):
        if self.kwargs.get('username'):
            return Tweet.objects.filter(owner__iexact=self.kwargs.get('username'))


class DateRangeTweetsView(generics.ListAPIView):
    """ Returns a list of all tweets in a specific date range. """
    model = Tweet
    serializer_class = TweetSerializer

    def get_queryset(self):
        if self.kwargs.get('date'):
            return Tweet.objects.filter(creation_date__gte=self.kwargs.get('date'))


class TextTweetsView(generics.ListAPIView):
    """ Returns a list of all tweets containing a specific text. """
    model = Tweet
    serializer_class = TweetSerializer

    def get_queryset(self):
        if self.kwargs.get('text'):
            return Tweet.objects.filter(text__icontains=self.kwargs.get('text'))


class HashtagTweetsView(generics.ListAPIView):
    """ Returns a list of all tweets containing a specific hashtag. """
    model = Tweet
    serializer_class = TweetSerializer

    def get_queryset(self):
        hashtag = self.kwargs.get('hashtag')
        if hashtag:
            hashtag = "#" + hashtag if hashtag[0] != "#" else hashtag
            return Tweet.objects.filter(Q(hashtags__name__iexact=hashtag))


# ########### Creation Endpoints ########### #
class FetchTweetsView(generics.ListCreateAPIView):
    """ Fetches 200 most recent tweets from a specific user and stores them in the DB. """
    model = Tweet
    serializer_class = TweetSerializer

    def get_queryset(self):
        if self.kwargs.get('username'):
            return Tweet.objects.filter(owner__iexact=self.kwargs.get('username'))


@login_required
def index(request):
    print("Logged in user:", request.user)

    return render(request, "tweet_monitor/index.html", {"name": request.user.first_name})


@login_required
def add_handle(request):
    """
    Gets the user inserted Twitter handle and fetches his/her 200 more recent tweets, storing them in the DB.
    :param request: The HTTP request.
    :return: Redirects back to index view with the result message.
    """
    if request.POST:
        handle = request.POST.get("handleName")

        if handle:
            found = Tweet.objects.filter(owner__iexact=handle)
            if found:
                messages.error(request, "The handle {} was already added to the database!".format(handle))
            else:
                user_obj = UserSocialAuth.objects.get(user_id=request.user.id)
                tweepy_handler = generate_tweepy_handler(user_obj.extra_data['access_token']['oauth_token'],
                                                         user_obj.extra_data['access_token']['oauth_token_secret'])

                try:
                    statuses = tweepy_handler.user_timeline(screen_name=handle, count=200)
                    tweets_list = []

                    for status in statuses:
                        tweet = Tweet(provider_id=status.id, owner=status.user.screen_name, text=status.text,
                                      creation_date=status.created_at)
                        tweets_list.append(tweet)

                    Tweet.objects.bulk_create(tweets_list)

                    saved_tweets = Tweet.objects.filter(owner__iexact=handle)
                    for t in saved_tweets:
                        t.extract_hashtags()

                    messages.success(request, "The handle {} was added!".format(handle))
                except TweepError as err:
                    if err.response.status_code == 404:
                        messages.error(request, "The provided Twitter handle doesn't exist. Please check the spelling.")
                    else:
                        messages.error(request, "There was a problem in the request, please check the handle spelling "
                                                "and try again.")
        else:
            messages.error(request, "Please provide a Twitter handle to have its tweets fetched.")
    else:
        messages.error(request, "There was a problem in the request, please try again.")

    return HttpResponseRedirect(reverse("tweet_monitor:index"))


@login_required
def filters(request):
    hashtags = Hashtag.objects.all()
    return render(request, "tweet_monitor/filters.html", {"name": request.user.first_name, "hashtags": hashtags})


@login_required
def process_filter(request):
    if request.POST:
        if request.POST.get("userFilter"):
            print("User:", request.POST.get("userFilter"))
            tweets = Tweet.objects.filter(owner__iexact=request.POST.get("userFilter"))
        elif request.POST.get("dateFilter"):
            print("Date:", request.POST.get("dateFilter"))
        elif request.POST.get("textFilter"):
            print("Text:", request.POST.get("textFilter"))
            tweets = Tweet.objects.filter(text__icontains=request.POST.get("textFilter"))
        elif request.POST.get("hashtagFilter"):
            print("Hashtag:", request.POST.get("hashtagFilter"))
            tweets = Tweet.objects.filter(Q(hashtags__name__iexact=request.POST.get("hashtagFilter")))
            print("Tweets found:", tweets)
    else:
        messages.error(request, "There was a problem in the request, please try again.")

    hashtags = Hashtag.objects.all()
    return render(request, "tweet_monitor/filters.html", {"name": request.user.first_name, "hashtags": hashtags,
                                                          "tweets": tweets})
    # return HttpResponseRedirect(reverse("tweet_monitor:filters"))


def generate_tweepy_handler(user_access_token, user_access_token_secret):
    """
    Generate handler object to use Tweepy's methods.
    :param user_access_token: The access token obtained from the signin process.
    :param user_access_token_secret: The access token secret.
    :return: The API handler.
    """
    consumer_key = settings.SOCIAL_AUTH_TWITTER_KEY
    consumer_secret = settings.SOCIAL_AUTH_TWITTER_SECRET
    access_key = user_access_token
    access_secret = user_access_token_secret
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    handler = tweepy.API(auth)

    return handler
