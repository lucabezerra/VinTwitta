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

# from ..tweet_monitor.models import Tweet, Hashtag
# from ..tweet_monitor.serializers import TweetSerializer, HashtagSerializer


def twitter_login(request):
    print(":::: REQUEST:", request)
    import ipdb; ipdb.set_trace()

    return HttpResponseRedirect(reverse("tweet_monitor:index"))
