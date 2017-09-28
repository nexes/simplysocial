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

        message = req_json.get('message')
        if message is None or len(message) > 255:
            return JSONResponse.new(code=400, message='message bad data: {}'.format(message))

        try:
            post = Posts.objects.get(post_id__exact=req_json.get('postid'))
            user = Users.objects.get(user_id__exact=req_json.get('userid'))
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='post {} or user {} was not found'.format(req_json.get('postid'), req_json.get('userid')))

        if user.is_active is False:
            return JSONResponse.new(code=400, message='user id {} must be logged in'.format(user.user_id))

        comment = Comments()
        comment.comment_id = uuid4().time_mid
        comment.author_id = user.user_id
        comment.author_name = user.user_name
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

        if user.is_active is False:
            return JSONResponse.new(code=400, message='user id {} must be logged in'.format(user.user_id))

        if user.user_id != comment.author_id:
            return JSONResponse.new(code=400, message='user {} is not the authoer of comment {}'.format(user.user_id, comment.author_id))

        comment.delete()
        return JSONResponse.new(code=200, message='success', commentid=comment.comment_id)



class CommentLike(View):
    """ Return or update the like count for the comment
        GET: returned json object {
            'count': the like count
        }
        POST: required json object {
            'userid': the user id of the user who is liking the comment,
            'commentid': the comment the user is liking
        }
        POST: returned json object {
            'count': the new like count
        }
    """
    def get(self, request: HttpRequest, commentid: str):
        commentid = int(commentid)

        try:
            comment = Comments.objects.get(comment_id__exact=commentid)
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='comment id {} is not found'.format(commentid))

        return JSONResponse.new(code=200, message='success', count=comment.like_count)

    def post(self, request: HttpRequest):
        try:
            req_json = json.loads(request.body.decod('UTF-8'))
        except json.JSONDecodeError:
            return JSONResponse.new(code=400, message='json decode error, bad data sent to the server')

        try:
            user = User.objects.get(user_id__exact=req_json.get('userid'))
            comment = Comments.objects.get(comment_id__exact=req_json.get('commentid'))
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='userid {} or commentid {} is not found'.format(req_json.get('userid'), req_json.get('commentid')))

        if user.is_active is False:
            return JSONResponse.new(code=400, message='user id {} must be logged in'.format(user.user_id))

        comment.like_count += 1
        comment.save()
        return JSONResponse.new(code=200, message='success', count=comment.like_count)
