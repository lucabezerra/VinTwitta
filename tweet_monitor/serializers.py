from rest_framework import serializers

from .models import Tweet, Hashtag


class HashtagSerializer(serializers.ModelSerializer):
    """
    Serializing all the Hashtags
    """
    class Meta:
        model = Hashtag
        fields = ('name',)


class TweetSerializer(serializers.ModelSerializer):
    """
    Serializing all the Tweets
    """
    hashtags = HashtagSerializer(many=True)

    class Meta:
        model = Tweet
        fields = ('provider_id', 'text', 'owner', 'creation_date', 'hashtags')
