from django.conf.urls import url

from . import views

app_name = "tweet_monitor"

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^list/$', views.TweetsView.as_view(), name='tweets_list'),
    url(r'^add_handle/$', views.add_handle, name='add_handle'),
    url(r'^filters/$', views.filters, name='filters'),
    url(r'^process_filter/$', views.process_filter, name='process_filter'),

    url(r'^filters/user/(?P<username>\S+)', views.UserTweetsView.as_view(), name='tweets_by_username'),
    url(r'^filters/date/(?P<date>\S+)', views.DateRangeTweetsView.as_view(), name='tweets_by_date'),
    url(r'^filters/text/(?P<text>\S+)', views.TextTweetsView.as_view(), name='tweets_by_text'),
    url(r'^filters/hashtag/(?P<hashtag>\S+)', views.HashtagTweetsView.as_view(), name='tweets_by_hashtag'),
]
