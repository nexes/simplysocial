""" handling view requests for user data """
from django.http import HttpRequest, HttpResponse
from django.views import View

from user.models import Users


class UserCounts(View):
    """ request the count of posts, followers... e.g /count/posts """
    def get(self, request: HttpRequest):
        pass

class UserDescription(View):
    """ GET: returns the users personal description
        POST: updates the users personal description
    """
    def get(self, request: HttpRequest):
        pass

    def post(self, request: HttpRequest):
        pass

class UserFollowers(View):
    """ GET: can check if the user is following another user
        POST: can follow or unfollow a user
    """
    def get(self, request: HttpRequest):
        pass

    def post(self, request: HttpRequest):
        pass
