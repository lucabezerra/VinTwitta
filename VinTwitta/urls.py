from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

app_name = "vintwitta"

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^djangojs/', include('djangojs.urls')),

    url(r'^$', TemplateView.as_view(template_name='tweet_monitor/index.html'), name='home'),
    url(r"^tweets/", include("tweet_monitor.urls"), name="tweets"),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^oauth/', include('social_django.urls', namespace='social')),
]
