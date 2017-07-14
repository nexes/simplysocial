import json
from random import random
from datetime import datetime
from lifesnap.aws import AWS
from lifesnap.util import JSONResponse

from user.models import Users
from post.models import Posts
from django.views import View
from django.db.models import F
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
        new_post = Posts()

        try:
            req_json = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            return JSONResponse.new(code=400, message='request decode error, bad data sent to the server')

        try:
            user = Users.objects.get(user_id__exact=req_json['userid'])
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='user id {} is not found.'.format(req_json['userid']))

        #only signed in users can create posts
        if request.session.get('{}'.format(user.user_id), False) is False:
            return JSONResponse.new(code=400, message='user is not signed in')

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

        return JSONResponse.new(code=200, message='success', postid=new_post.post_id)



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
            return JSONResponse.new(code=400, message="request decode error, bad data sent to the server")

        try:
            user = Users.objects.get(user_id__exact=req_json.get('userid', ''))
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message="userid {} is not found".format(req_json['userid']))

        #check user is logged in via sessions
        if request.session.get('{}'.format(user.user_id), False) is False:
            return JSONResponse.new(code=400, message='user is not signed in')

        if req_json.get('postid') is None and req_json.get('title') is None:
            return JSONResponse.new(code=400, message='postid or title must be present')

        try:
            if req_json.get('postid') is not None:
                post = user.posts_set.get(post_id__exact=int(req_json['postid']))

            elif req_json.get('title') is not None:
                post = user.posts_set.get(message_title__exact=req_json['title'])
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='postid {} is not found'.format(req_json['postid']))

        s3_bucket.remove_image(key_name=post.image_name)
        post.delete()

        return JSONResponse.new(code=200, message='success', postcount=user.posts_set.count())



class PostUpdate(View):
    """ Updates a post title or message. Cannot update a posts image
        POST: required json object {
            'userid': the userid of the logged in user,
            'postid': the postid from the post that will be updated
            'title': if this is not empty, the title will be updated,
            'message': if this is not empty, the message will be updated,
        }
    """
    def post(self, request: HttpRequest):
        try:
            req_json = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            return JSONResponse.new(code=400, message='request decode error, bad data sent to the server')

        if request.session.get('{}'.format(req_json['userid']), False) is False:
            return JSONResponse.new(code=400, message='userid {} is not logged in to update post {}'.format(req_json['userid'], req_json['postid']))

        try:
            user = Users.objects.get(user_id__exact=req_json['userid'])
            post = user.posts_set.get(post_id__exact=req_json['postid'])
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='userid {} or postid {} was not found'.format(req_json['userid'], req_json['postid']))

        new_title = req_json.get('title')
        new_message = req_json.get('message')

        if new_title is not None:
            if len(new_title) <= 100:
                post.message_title = new_title
            else:
                return JSONResponse.new(code=400, message='title length incorrect {}'.format(len(new_title)))

        if new_message is not None:
            if len(new_message) <= 254:
                post.message = new_message
            else:
                return JSONResponse.new(code=400, message='message length incorrect {}'.format(len(new_message)))

        post.save(update_fields=['message_title', 'message'])
        p = dict({
            'postid': post.post_id,
            'message': post.message,
            'title': post.message_title,
            'views': post.view_count,
            'likes': post.like_count,
            'imageurl': post.image_url,
            'date': post.creation_date.isoformat()
        })
        return JSONResponse.new(code=200, message='success', post=p)



class PostSearchTitle(View):
    """ returned posts from search results
        GET: search for posts given the search parameters
        returned json object: {
            'code': http status_code,
            'message': 'server message, 'success' or 'error message',
            'post': [array of json objects {
                'postid': the postid,
                'message': post message,
                'title': post title,
                'views': view count,
                'likes': like count,
                'imageurl': the http url where the image can be found,
                'date': the date the post was created
            }]
        }
    """
    def get(self, request: HttpRequest, userid: str, title: str, count: str):
        count = int(count)
        if count < 0:
            count *= -1

        try:
            user = Users.objects.get(user_id__exact=userid)
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='userid {} is not found'.format(userid))

        posts = user.posts_set.filter(message_title__icontains=title)[:count]
        post_list = []

        for post in posts:
            p = dict({
                'postid': post.post_id,
                'message': post.message,
                'title': post.message_title,
                'views': post.view_count,
                'likes': post.like_count,
                'imageurl': post.image_url,
                'date': post.creation_date.isoformat()
            })
            post_list.append(p)
        return JSONResponse.new(code=200, message='success', posts=post_list)



class PostSearchDate(View):
    """ return posts from the specified time
        GET: search for posts up to count from time_stamp until now.
             time_stamp: should be an integer. Send your date using datetime.timestamp()

        returned json object: {
            'code': http status_code,
            'message': 'server message, 'success' or 'error message',
            'post': [array of json objects {
                'postid': post id,
                'message': post message,
                'title': post title,
                'views': view count,
                'likes': like count,
                'imageurl': the http url where the image can be found,
                'date': the date the post was created
            }]
        }
    """
    def get(self, request: HttpRequest, userid: str, time_stamp: str, count: str):
        count = int(count)
        if count < 0:
            count *= -1

        try:
            user = Users.objects.get(user_id__exact=userid)
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='userid {} is not found'.format(userid))

        try:
            # we can cast to an int because we dont need anymore percision than month and year
            search_date = datetime.fromtimestamp(int(time_stamp))
        except (OverflowError, OSError):
            return JSONResponse.new(code=400, message='recieved incorrect time stamp {}'.format(time_stamp))

        posts = user.posts_set.filter(creation_date__date__gt=datetime.date(search_date))[:count]
        post_list = []

        for post in posts:
            p = dict({
                'postid': post.post_id,
                'message': post.message,
                'title': post.message_title,
                'views': post.view_count,
                'likes': post.like_count,
                'imageurl': post.image_url,
                'date': post.creation_date.isoformat()
            })
            post_list.append(p)
        return JSONResponse.new(code=200, message='success', posts=post_list)



class PostLike(View):
    """ return the like count of a post, or update the like count to a post
        GET: returned json object {
            'postid': the post id,
            'like': the like count
        }
        POST: required json object {
            'postid': postid
        }
        POST: returned json object {
            'code': http status code,
            'message': success message,
            'likecount': updated like count
        }
    """
    def get(self, request: HttpRequest, postid: str):
        postid = int(postid)

        try:
            post = Posts.objects.get(post_id__exact=postid)
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='postid {} was not found'.format(postid))

        return JSONResponse.new(code=200, message='success', postid=post.post_id, like=post.like_count)

    def post(self, request: HttpRequest):
        try:
            req_json = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            return JSONResponse.new(code=400, message='json decode error, bad data sent to the server')

        try:
            post = Posts.objects.get(post_id__exact=req_json['postid'])
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='postid {} is not found'.format(req_json['postid']))

        post.like_count += 1
        post.save(update_fields=['like_count'])

        return JSONResponse.new(code=200, message='success', likecount=post.like_count)
