""" handles authenticating a user, or creating/deleting a new user """
from user.models import Users

from django.http import HttpRequest
from django.views import View


class AuthUserLogin(View):
    """ authenticate a users login request """
    def post(self, request: HttpRequest):
        pass

class AuthUserCreate(View):
    """ authenticate a new users request """
    def post(self, request: HttpRequest):
        pass

class AuthUserDelete(View):
    """ authenticate a users delete request """
    def post(self, request: HttpRequest):
        pass
