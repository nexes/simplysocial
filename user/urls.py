""" url pattern for user routes """
from user.views import UserCounts, UserDescription, UserFollowers
from django.conf.urls import url


app_name = 'user'

urlpatterns = [
    url(r'^count/(?P<count_type>[a-zA-Z]+)/$', UserCounts.as_view(), name='count'),
    url(r'^description/$', UserDescription.as_view(), name='description'),
    url(r'^newfollow/$', UserFollowers.as_view(), name='newfollower'),
    url(r'^removefollow/$', UserFollowers.as_view(), name='removefollower'),
]