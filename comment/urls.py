from comment.views import CommentCreate, CommentDelete
from django.conf.urls import url


app_name = 'comment'

urlpatterns = [
    url(r'^create/$', CommentCreate.as_view(), name='create'),
    url(r'^delete/$', CommentDelete.as_view(), name='delete')
]
