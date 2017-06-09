import json

from decouple import config
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from social_django.models import UserSocialAuth
import tweepy
from tweepy import TweepError

from .models import Tweet, Hashtag
from .serializers import TweetSerializer, HashtagSerializer


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


class HashtagsView(generics.ListAPIView):
    """ Returns a list of all hashtags. """
    model = Hashtag
    serializer_class = HashtagSerializer

    def get_queryset(self):
        return Hashtag.objects.all()


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
class FetchTweetsView(APIView):
    """ Fetches 200 most recent tweets from a specific user and stores them in the DB. """

    def post(self, request):
        username = request.data.get('username')
        if username:
            response = _add_handle(request.data.get("user_id"), username)
        else:
            response = "Please provide a Twitter handle to have its tweets fetched."

        return Response(response)


def _add_handle(user_id, handle):

    found = Tweet.objects.filter(owner__iexact=handle)
    if found:
        return_message = "The handle {} was already added to the database!".format(handle)
    else:
        user_obj = UserSocialAuth.objects.get(user_id=user_id)
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

            return_message = "The handle {} was added!".format(handle)
        except TweepError as err:
            if err.response.status_code == 404:
                return_message = "The provided Twitter handle doesn't exist. Please check the spelling."
            else:
                return_message = "There was a problem in the request, please check the handle spelling and try again."

    return return_message


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


@login_required
def index(request):
    payload = {
        "name": request.user.first_name,
        "local_storage": {
            "sessionid": request.COOKIES.get("sessionid"),
            "csrftoken": request.COOKIES.get("csrftoken")
        }
    }

    return render(request, "tweet_monitor/react_index.html", payload)


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
                messages.warning(request, "{}' tweets were already in the database!".format(handle))
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

                    messages.success(request, "{}' were added successfully!".format(handle))
                except TweepError as err:
                    print(":::: ERROR:", err, err.response.status_code)
                    if err.response.status_code == 404:
                        messages.error(request, "The provided Twitter handle doesn't exist. Please check the spelling.")
                    elif err.response.status_code == 401:
                        messages.error(request, "{}'s timeline is protected, we can't fetch his/her "
                                                "tweets.".format(handle))
                    else:
                        messages.error(request, "There was a problem in the request, please check the handle spelling "
                                                "and try again.")
        else:
            messages.error(request, "Please provide a Twitter handle to have its tweets fetched.")
    else:
        messages.error(request, "There was a problem in the request, please try again.")

    return HttpResponseRedirect(reverse("tweet_monitor:index"))


# ################### FOR TESTING PURPOSES ONLY ################### #

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
