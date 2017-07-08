from post.views import PostCreate, PostDelete, PostUpdate, PostSearch
from django.conf.urls import url


app_name = 'post'

urlpatterns = [
    url(r'^create/$', PostCreate.as_view(), name='create'),
    url(r'^delete/$', PostDelete.as_view(), name='delete'),
    url(r'^update/$', PostUpdate.as_view(), name='update'),
    url(r'^search/title/(?P<userid>[0-9]+)/(?P<title>[\W\w]+)/(?P<count>[0-9]+)/$', PostSearch.as_view(), name='searchtitle')
]
