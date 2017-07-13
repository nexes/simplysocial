from post.views import PostCreate, PostDelete, PostUpdate, PostSearchTitle, PostSearchDate
from django.conf.urls import url


app_name = 'post'

urlpatterns = [
    url(r'^create/$', PostCreate.as_view(), name='create'),
    url(r'^delete/$', PostDelete.as_view(), name='delete'),
    url(r'^update/$', PostUpdate.as_view(), name='update'),
    url(r'^search/title/(?P<userid>[0-9]+)/(?P<title>[\W\w]+)/(?P<count>[0-9]+)/$', PostSearchTitle.as_view(), name='searchtitle'),
    url(r'^search/range/(?P<userid>[0-9]+)/(?P<time_stamp>[0-9]+)/(?P<count>[0-9]+)/$', PostSearchDate.as_view(), name='searchdate')
]