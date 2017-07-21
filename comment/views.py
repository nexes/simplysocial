import json
from uuid import uuid4
from user.models import Users
from post.models import Posts
from comment.models import Comments
from lifesnap.util import JSONResponse
from django.views import View
from django.http import HttpRequest
from django.core.exceptions import ObjectDoesNotExist


class CommentCreate(View):
    """ Create a comment for a post
        required json object {
            'postid': the id of the post to comment,
            'userid': the user id of the author of the comment,
            'message': the comment itself
        }
        returned json object {
            'commentid': the new comment id
        }
    """
    def post(self, request: HttpRequest):
        try:
            req_json = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            return JSONResponse.new(code=400, message='json decode error, bad data sent to the server')

        if request.session.get('{}'.format(req_json.get('userid')), False) is False:
            return JSONResponse.new(code=400, message='user {} is not signed in'.format(req_json.get('userid')))

        message = req_json.get('message')
        if message is None or len(message) > 255:
            return JSONResponse.new(code=400, message='message bad data: {}'.format(message))

        try:
            post = Posts.objects.get(post_id__exact=req_json.get('postid'))
            user = Users.objects.get(user_id__exact=req_json.get('userid'))
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='post {} or user {} was not found'.format(req_json.get('postid'), req_json.get('userid')))

        comment = Comments()
        comment.comment_id = uuid4().time_mid
        comment.author_id = user.user_id
        comment.message = message
        comment.save()
        post.comments_set.add(comment)

        return JSONResponse.new(code=200, message='success', commentid=comment.comment_id)


class CommentDelete(View):
    """ Delete a comment from a post
        required json object {
            'userid': the id of the user who owns the comment,
            'commentid': the id of the comment to delete
        }
    """
    def post(self, request: HttpRequest):
        try:
            req_json = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
           return JSONResponse.new(code=400, message='json decode error, bad data sent to the server')

        try:
            user = Users.objects.get(user_id__exact=req_json.get('userid'))
            comment = Comments.objects.get(comment_id__exact=req_json.get('commentid'))
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='user {} or comment {} is not found'.format(req_json.get('userid'), req_json.get('commentid')))

        if request.session.get('{}'.format(user.user_id), False) is False:
            return JSONResponse.new(code=400, message='user {} is not signed in'.format(user.user_id))

        if user.user_id != comment.author_id:
            return JSONResponse.new(code=400, message='user {} is not the authoer of comment {}'.format(user.user_id, comment.author_id))

        comment.delete()
        return JSONResponse.new(code=200, message='success', commentid=comment.comment_id)
