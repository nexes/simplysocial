from random import random
from lifesnap.aws import AWS
import json

from user.models import Users
from post.models import Posts
from django.views import View
from django.http import HttpRequest, JsonResponse
from django.core.exceptions import ObjectDoesNotExist



class PostCreate(View):
    """ a signed in user can create a new post
        POST: required json object {
            'image': the photo to post, the front end will encode to base64 before sending.
            'message': optional - if you want a message with the photo,
            'title': optional - if you want to title your post,
            'userid': the users user_id
        }
    """
    def post(self, request: HttpRequest):
        s3_bucket = AWS('snap-life')
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
        image_name = '{}{}.png'.format(user.user_id, new_post.post_id)

        url = s3_bucket.upload_image(image_name, req_json['image'])

        new_post.message = req_json.get('message', '')
        new_post.message_title = req_json.get('title', '')
        new_post.image_name = image_name
        new_post.image_url = url
        new_post.save()
        user.posts_set.add(new_post)

        resp.content = json.dumps({
            'message': 'success'
        })
        return resp


#TODO: refactor all of these resp.status_code resp.content stuff DRY DRY DRY
class PostDelete(View):
    """ Delete a post if found, postid and title are optional but one needs to be set
        Post: required json object: {
            userid: user id,
            postid: <optional> can search by post id,
            title: <optional> can search by post title,
        }
        if both postid and title is present, postid will be prefered.
    """
    def post(self, request: HttpRequest):
        s3_bucket = AWS('snap-life')
        resp = JsonResponse({})
        resp.status_code = 200

        try:
            req_json = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            resp.status_code = 400
            resp.content = json.dumps({
                "message": "request decode error, bad data sent to the server"
                })
            return resp

        try:
            user = Users.objects.get(user_id__exact=req_json.get('userid', ''))
        except ObjectDoesNotExist:
            resp.status_code = 400
            resp.content = json.dumps({
                "message": "userid {} is not found".format(req_json['userid'])
                })
            return resp

        #check user is logged in via sessions
        if request.session.get('{}'.format(user.user_id), False) is False:
            resp.status_code = 400
            resp.content = json.dumps({
                'message': 'user is not signed in'
            })
            return resp

        if req_json.get('postid') is None and req_json.get('title') is None:
            resp.status_code = 400
            resp.content = json.dumps({
                'message': 'postid or title must be present'
            })
            return resp

        if req_json.get('postid') is not None:
            try:
                post = user.posts_set.get(post_id__exact=int(req_json['postid']))
            except ObjectDoesNotExist:
                resp.status_code = 400
                resp.content = json.dumps({
                    'message': 'postid {} is not found'.format(req_json['postid'])
                })
                return resp
        elif req_json.get('title') is not None:
            try:
                post = user.posts_set.get(message_title__exact=req_json['title'])
            except ObjectDoesNotExist:
                resp.status_code = 400
                resp.content = json.dumps({
                    'message': 'post with title {} is not found'.format(req_json['title'])
                })
                return resp

        s3_bucket.remove_image(key_name=post.image_name)
        post.delete()

        resp.content = json.dumps({
            'message': 'success',
            'postcount': '{}'.format(user.posts_set.count())
        })
        return resp


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
