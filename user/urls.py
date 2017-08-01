""" url pattern for user routes """
from user.views import (
    UserCounts, UserDescription, UserFollowAdd, UserFollowRemove, UserProfileUpdate, UserOnline
)
from django.conf.urls import url


app_name = 'user'

urlpatterns = [
    url(r'^count/(?P<user_id>[0-9]+)/(?P<count_type>[a-zA-Z]+)/$', UserCounts.as_view(), name='count'),
    url(r'^description/(?P<user_id>[0-9]+)/$', UserDescription.as_view(), name='get_description'),
    url(r'^online/(?P<username>[a-zA-Z0-9]+)/$', UserOnline.as_view(), name='online'),
    url(r'^description/$', UserDescription.as_view(), name='set_description'),
    url(r'^profile/update/$', UserProfileUpdate.as_view(), name='profileupdate'),
    url(r'^follow/new/$', UserFollowAdd.as_view(), name='newfollower'),
    url(r'^follow/remove/$', UserFollowRemove.as_view(), name='removefollower')
]
