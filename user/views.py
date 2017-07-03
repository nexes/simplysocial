""" handling view requests for user data """
from user.models import Users
import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, JsonResponse
from django.views import View



class UserCounts(View):
    """ request the count of posts, followers... e.g /count/posts """
    def get(self, request: HttpRequest, user_id: int, count_type: str):
        resp = JsonResponse({})

        try:
            user = Users.objects.get(user_id__exact=user_id)
        except ObjectDoesNotExist:
            resp.status_code = 400
            resp.content = json.dumps({
                'message': 'bad user id {}, user not found'.format(user_id)
            })
            return resp

        if count_type.lower() == 'posts':
            count = user.posts_set.count()
            resp.status_code = 200
            resp.content = json.dumps({
                'count': count
            })
        elif count_type.lower() == 'followers':
            # TODO - this needs to be done when we create followers model
            resp.status_code = 200
            resp.content = json.dumps({
                'followers': 3
            })

        return resp


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
