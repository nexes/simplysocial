from random import random
import json

from user.models import Users
from post.models import Posts
from django.views import View
from django.http import HttpRequest, JsonResponse
from django.core.exceptions import ObjectDoesNotExist



class PostCreate(View):
    """ a signed in user can create a new post
        POST: required json object {
            'image': the photo to post,
            'message': optional - if you want a message with the photo,
            'userid': the users user_id
        }
    """
    def post(self, request: HttpRequest):
        resp = JsonResponse({})
        resp.status_code = 200
        new_post = Posts()

        try:
            req_json = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            resp.status_code = 400
            resp.content = json.dumps({
                "message": "request decode error, bad data sent to the server"
                })
            return resp

        try:
            user = Users.objects.get(user_id__exact=req_json['userid'])
        except ObjectDoesNotExist:
            resp.status_code = 400
            resp.content = json.dumps({
                "message": "userid {} is not found".format(req_json['userid'])
                })
            return resp

        #only signed in users can create posts
        if request.session.get('{}'.format(user.user_id), False) is False:
            resp.status_code = 400
            resp.content = json.dumps({
                'message': 'user is not signed in'
            })
            return resp

        #create new post and assign to the user
        new_post.post_id = int(random() * 1000000)
        new_post.image_url = 'we need to setup s3 bucket url',
        new_post.message = req_json['message']
        new_post.save()
        user.posts_set.add(new_post)

        resp.content = json.dumps({
            'message': 'success'
        })
        return resp


class PostDelete(View):
    """  """
    def post(self, request: HttpRequest):
        pass


class PostUpdate(View):
    """  """
    def post(self, request: HttpRequest):
        pass


class PostSearch(View):
    """ returned posts from search results
        GET: search: username, title
    """
    def get(self, request: HttpRequest, search: str, count: int):
        if 'username' in request.path:
            pass
        elif 'title' in request.path:
            pass
