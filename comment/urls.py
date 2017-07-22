from comment.views import CommentCreate, CommentDelete, CommentLike
from django.conf.urls import url


app_name = 'comment'

urlpatterns = [
    url(r'^create/$', CommentCreate.as_view(), name='create'),
    url(r'^delete/$', CommentDelete.as_view(), name='delete'),
    url(r'^count/like/$', CommentLike.as_view(), name='setlike'),
    url(r'^count/like/(?P<commentid>[0-9]+)/$', CommentLike.as_view(), name='getlike')
]
