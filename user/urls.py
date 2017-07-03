""" url pattern for user routes """
from user.views import UserCounts, UserDescription, UserFollowers
from django.conf.urls import url


app_name = 'user'

urlpatterns = [
    url(r'^count/(?P<user_id>[0-9]+)/(?P<count_type>[a-zA-Z]+)/$', UserCounts.as_view(), name='count'),
    url(r'^description/$', UserDescription.as_view(), name='description'),
    url(r'^follow/new/$', UserFollowers.as_view(), name='newfollower'),
    url(r'^follow/remove/$', UserFollowers.as_view(), name='removefollower'),
]
