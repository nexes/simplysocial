""" url pattern for user auth routes """
from django.conf.urls import url
from userauth.views import AuthUserLogin, AuthUserCreate, AuthUserDelete


app_name = 'userauth'

urlpatterns = [
    url(r'^user/login/', AuthUserLogin.as_view(), name='login'),
    url(r'^user/create/', AuthUserCreate.as_view(), name='create'),
    url(r'^user/delete/', AuthUserDelete.as_view(), name='delete')
]
