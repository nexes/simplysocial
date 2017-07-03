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
    """ get or set the users description
        GET: apiurl/<the user if>/
        POST: required json object {
            'userid': the user id,
            'description': 'a string that is the new description 0 < desciption < 255'
        }
    """
    def get(self, request: HttpRequest, user_id: int):
        resp = JsonResponse({})

        try:
            user = Users.objects.get(user_id__exact=user_id)
        except ObjectDoesNotExist:
            resp.status_code = 400
            resp.content = json.dumps({
                'meesage': 'bad user id {}, user not found'.format(user_id)
            })
            return resp

        description = user.about
        resp.status_code = 200
        resp.content = json.dumps({
            'message': description
        })

        return resp

    def post(self, request: HttpRequest):
        resp = JsonResponse({})
        resp.status_code = 200
        req_body = json.loads(request.body.decode('UTF-8'))

        try:
            user = Users.objects.get(user_id__exact=req_body['userid'])
        except ObjectDoesNotExist:
            resp.status_code = 400
            resp.content = json.dumps({
                'meesage': 'bad user id {}, user not found'.format(req_body['userid'])
            })
            return resp

        new_desc = req_body['description']
        if len(new_desc) < 1 or len(new_desc) > 255:
            resp.status_code = 400
            resp.content = json.dumps({
                'message': 'description doesn\'t meet the length requirements: {}'.format(len(new_desc))
            })
            return resp
        else:
            user.about = new_desc
            user.save(update_fields=['about'])

        resp.content = json.dumps({
            'message': 'success'
        })
        return resp


class UserFollowers(View):
    """ GET: can check if the user is following another user
        POST: can follow or unfollow a user
    """
    def get(self, request: HttpRequest):
        pass

    def post(self, request: HttpRequest):
        pass
