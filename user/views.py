""" handling view requests for user data """
from lifesnap.util import JSONResponse
from user.models import Users
import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, JsonResponse
from django.views import View



class UserCounts(View):
    """ request the count of posts, followers... e.g /count/posts """
    def get(self, request: HttpRequest, user_id: int, count_type: str):
        try:
            user = Users.objects.get(user_id__exact=user_id)
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='bad user id {}, user not found'.format(user_id))

        if count_type.lower() == 'posts':
            count = user.posts_set.count()

        elif count_type.lower() == 'followers':
            # TODO - this needs to be done when we create followers model
            count = 23 #get this from followers

        return JSONResponse.new(code=200, message='success', count=count)


class UserDescription(View):
    """ get or set the users description
        GET: apiurl/<the user id>/
        POST: required json object {
            'userid': the user id,
            'description': 'a string that is the new description 0 < desciption < 255'
        }
    """
    def get(self, request: HttpRequest, user_id: int):
        try:
            user = Users.objects.get(user_id__exact=user_id)
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='bad user id {}, user not found'.format(user_id))

        description = user.about
        return JSONResponse.new(code=200, message='success', description=description)

    def post(self, request: HttpRequest):
        req_body = json.loads(request.body.decode('UTF-8'))

        try:
            user = Users.objects.get(user_id__exact=req_body['userid'])
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='bad user id {}, user not found'.format(req_body['userid']))

        new_desc = req_body['description']
        if len(new_desc) < 1 or len(new_desc) > 255:
            return JSONResponse.new(code=400, message='description doesn\'t meet the length requirements: {}'.format(len(new_desc)))

        user.about = new_desc
        user.save(update_fields=['about'])
        return JSONResponse.new(code=200, message='success')


class UserFollowers(View):
    """ GET: can check if the user is following another user
        POST: can follow or unfollow a user
    """
    def get(self, request: HttpRequest):
        #TODO - after we setup the followers model
        pass

    def post(self, request: HttpRequest):
        #TODO - after we setup the followers model
        pass
