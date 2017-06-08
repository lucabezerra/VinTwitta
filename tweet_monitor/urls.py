from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

app_name = "tweet_monitor"

urlpatterns = [
    # React view
    url(r'^process_add_handle/$', views.add_handle, name='add_handle'),
    url(r'^$', TemplateView.as_view(template_name='tweet_monitor/react_index.html'), name='index'),


    # Pure Django views
    url(r'^index/$', views.index, name='index2'),  # TODO: EDIT BACK
    url(r'^list/$', views.TweetsView.as_view(), name='tweets_list'),
    # url(r'^add_handle/$', views.add_handle, name='add_handle'),
    # url(r'^filters/$', views.filters, name='filters'),
    url(r'^process_filter/$', views.process_filter, name='process_filter'),

    # DRF views
    url(r'^filters/user/(?P<username>\S+)/$', views.UserTweetsView.as_view(), name='tweets_by_username'),
    url(r'^filters/date/(?P<date>\S+)/$', views.DateRangeTweetsView.as_view(), name='tweets_by_date'),
    url(r'^filters/text/(?P<text>\S+)/$', views.TextTweetsView.as_view(), name='tweets_by_text'),
    url(r'^filters/hashtag/(?P<hashtag>\S+)$/', views.HashtagTweetsView.as_view(), name='tweets_by_hashtag'),

    # url(r'^filters/user/(?P<username>\S+)/$', views.UserTweetsView.as_view(), name='tweets_by_username'),
    # url(r'^filters/date/(?P<date>\S+)/$', views.DateRangeTweetsView.as_view(), name='tweets_by_date'),
    # url(r'^filters/text/(?P<text>\S+)/$', views.TextTweetsView.as_view(), name='tweets_by_text'),
    # url(r'^filters/hashtag/(?P<hashtag>\S+)$/', views.HashtagTweetsView.as_view(), name='tweets_by_hashtag'),

    url(r'^fetch/$', views.FetchTweetsView.as_view(), name='fetch_tweets'),

    url(r'^.*/', TemplateView.as_view(template_name="tweet_monitor/react_index.html"), name='react_base'),
]
