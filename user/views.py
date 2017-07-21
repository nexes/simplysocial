""" handling view requests for user data """
import json
from lifesnap.aws import AWS
from user.models import Users
from lifesnap.util import JSONResponse

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.views import View



class UserCounts(View):
    """ request the following count
        /apiendpoint/posts/ - return the number of posts the user has made
        /apiendpoint/followers/ - return the number of people following the user
        /apiendpoint/following/ - return the number of people the user is following
    """
    def get(self, request: HttpRequest, user_id: int, count_type: str):
        try:
            user = Users.objects.get(user_id__exact=user_id)
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='bad user id {}, user not found'.format(user_id))

        if count_type.lower() == 'posts':
            count = user.posts_set.count()

        elif count_type.lower() == 'followers':
            count = user.follower_count

        elif count_type.lower() == 'following':
            count = user.following.count()

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
        try:
            req_json = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            return JSONResponse.new(code=400, message='json decode error, bad data sent to the server')

        try:
            user = Users.objects.get(user_id__exact=req_json['userid'])
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='bad user id {}, user not found'.format(req_json['userid']))

        new_desc = req_json.get('description', '')
        if len(new_desc) < 1 or len(new_desc) > 255:
            return JSONResponse.new(code=400, message='description doesn\'t meet the length requirements: {}'.format(len(new_desc)))

        user.about = new_desc
        user.save(update_fields=['about'])
        return JSONResponse.new(code=200, message='success')



class UserFollowAdd(View):
    """ Add a new follower: user must be logged in to add new followers
        required json object: {
            'userid': the user id of the user who will add a new follower,
            'username': the username of the person we want to follow
        }
        returned json object: {
            'followercount': the new follower count
        }
    """
    def post(self, request: HttpRequest):
        try:
            req_json = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            return JSONResponse.new(code=400, message='json decode error, bad data sent to the server')

        if request.session.get('{}'.format(req_json.get('userid')), False) is False:
            return JSONResponse.new(code=400, message='user {} is not signed in'.format(req_json['userid']))

        try:
            user = Users.objects.get(user_id__exact=req_json['userid'])
            follower = Users.objects.get(user_name__exact=req_json['username'])
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='userid {} or username {} not found'.format(req_json['userid'], req_json['username']))

        user.following.add(follower)
        user.follower_count += 1
        user.save()
        return JSONResponse.new(code=200, message='success', followercount=user.follower_count)



class UserFollowRemove(View):
    """ Remove a follower: user must be logged in to remove a followers
        required json object: {
            'userid': the user id of the user who remove the follower,
            'username': the username of the user to remove,
        }
        returned json object: {
            'followercount': the new follower count
        }
    """
    def post(self, request: HttpRequest):
        try:
            req_json = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            return JSONResponse.new(code=400, message='json decode error, bad data sent to the server')

        if request.session.get('{}'.format(req_json.get('userid')), False) is False:
            return JSONResponse.new(code=400, message='user {} is not signed in'.format(req_json['userid']))

        try:
            user = Users.objects.get(user_id__exact=req_json.get('userid'))
            follower = user.following.get(user_name__exact=req_json.get('username'))
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='userid {} or username {} not found'.format(req_json['userid'], req_json['username']))

        user.follower_count -= 1
        user.following.remove(follower)
        user.save()
        return JSONResponse.new(code=200, message='success', followercount=user.follower_count)



class UserProfileUpdate(View):
    """ Update the users profile picture, the user must be logged in
        required json object: {
            'userid': the userid who wants to update the profile picture,
            'profilepic': the base64 encoded profile image
        }
        returned json object: {
            'url': the url for the profile picture. can be used inside <image>
        }
    """
    def post(self, request: HttpRequest):
        aws = AWS('snap-life')

        try:
            req_json = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            return JSONResponse.new(code=400, message='json decode error, bad data sent to the server')

        try:
            user = Users.objects.get(user_id__exact=req_json.get('userid'))
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='user {} is not found'.format(req_json.get('userid')))

        if request.session.get('{}'.format(req_json.get('userid')), False) is False:
            return JSONResponse.new(code=400, message='user {} is not signed in'.format(req_json['userid']))

        #is there a better way?
        aws.remove_profile_image('profilepics/{}.png'.format(user.user_name))
        url = aws.upload_profile_image('profilepic/{}.png'.format(user.user_name), req_json.get('profilepic'))

        user.profile_url = url
        user.save(update_fields=['profile_url'])
        return JSONResponse.new(code=200, message='success', url=url)
