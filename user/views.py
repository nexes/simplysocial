""" handling view requests for user data """
import json
from lifesnap.aws import AWS
from user.models import Users
from lifesnap.util import JSONResponse

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.utils import timezone
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


class UserFollowers(View):
    """ return a list of the users followers
        /apiendpoint/(userid or username) - the user id or username of the user we went to followers for.

        returned JSON object {
            'username': the username of the follower,
            'avatar': the url of the users avatar
        }
    """
    def get(self, request: HttpRequest, user_id: str):
        try:
            # lets check userID first
            user = Users.objects.get(user_id__exact=user_id)
        except ObjectDoesNotExist:
            try:
                # userID was not found, lets try username
                user = Users.objects.get(user_name__exact=user_id)
            except ObjectDoesNotExist:
                return JSONResponse.new(code=400, message='user {} is not found'.format(user_id))

        follow_users = []
        following = user.following.all()

        for follower in following:
            follow_users.append({
                'username': follower.user_name,
                'avatar': follower.profile_url
            })

        return JSONResponse.new(code=200, message='success', following=follow_users)


class UserOnline(View):
    """ request if the user is online
        /apiendpoint/(username) - return true or false if this username is currently logged in
    """

    def get(self, request: HttpRequest, username: str):
        try:
            user = Users.objects.get(user_name__exact=username)
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='user name {} is not found'.format(username))

        # if there is no session data, the user is either not logged in, or is accessing from outside the original session.
        # either way, a log in is required here
        if request.session.get('{}'.format(user.user_id), False) is False:
            user.is_active = False
            user.save()
            return JSONResponse.new(code=200, message='success', loggedin=False, userid=0)

        # If the user is still showing active after 24 hours, log the user off.
        uid = user.user_id
        now = timezone.now()
        delta_time = (now - user.last_login_date).total_seconds()
        if ((delta_time / 3600) / 24) >= 1:
            if '{}'.format(user.user_id) in request.session:
                del request.session['{}'.format(user.user_id)]

            user.is_active = False
            uid = 0
            user.save()

        return JSONResponse.new(code=200, message='success', loggedin=user.is_active, userid=uid)



class UserFriendSnapshot(View):
    """ This is similar to UserAccountSnapshot but for those a user is following (or may follow)
        return the requested users posts, account counts
        GET: /apiendpoint/(username)

        returned JSON object: {
            'about': the users account description,
            'postcount': the number of posts by the user,
            'following': the number of people the ueser is following,
            'followers': the number of people following the user,
            'avatar': the url to the users avatar,
            'posts': a list of the users posts {
                'message': the post message,
                'url': the url to the message image if there is one,
                'date': the date of the post,
                'likes': the posts like count
            },
            following: a list of who the user is following {
                'username': the users username,
                'avatar': the url to the users avatar
            }
        }
    """

    def get(self, request: HttpRequest, username: str):
        try:
            user = Users.objects.get(user_name__exact=username)
            posts = user.posts_set.all()
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='user {} was not found'.format(username))

        post_list = []
        for post in posts:
            post_list.append({
                'message': post.message,
                'url': post.image_url,
                'date': post.creation_date.isoformat(),
                'likes': post.like_count
            })

        following_list = []
        for follow_user in user.following.all():
            following_list.append({
                'username': follow_user.user_name,
                'avatar': follow_user.profile_url
            })

        return JSONResponse.new(
            code=200,
            message='success',
            about=user.about,
            postcount=posts.count(),
            following=user.following.count(),
            followers=user.follower_count,
            avatar=user.profile_url,
            posts=post_list,
            followinglist=following_list
        )


class UserAccountSnapshot(View):
    """ This is usefull instead of making several http calls
        request to get the the meta data of a users account
        GET: /apiendpoint/(userid)

        returned JSON object: {
            'firstname': users first name,
            'lastname': users last name,
            'email': users email address,
            'postcount': number of users posts,
            'following': following count,
            'followers': followers count,
            'description': users description,
            'avatar': url to users profile avatar,
            'startdate': users creation date
        }
    """

    def get(self, request: HttpRequest, user_id: int):
        try:
            user = Users.objects.get(user_id__exact=user_id)
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='bad user id {}, user not found'.format(user_id))

        if request.session.get('{}'.format(user.user_id), False) is False:
            return JSONResponse.new(code=400, message='user id {} must be logged in'.format(user.user_id))

        post_count = user.posts_set.count()
        following_count = user.following.count()
        return JSONResponse.new(
            code=200,
            message='success',
            username=user.user_name,
            firstname=user.first_name,
            lastname=user.last_name,
            email=user.email,
            description=user.about,
            avatar=user.profile_url,
            startdate=user.creation_date.isoformat(),
            followers=user.follower_count,
            following=following_count,
            postcount=post_count
        )


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
            user = Users.objects.get(user_id__exact=req_json.get('userid'))
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='bad user id {}, user not found'.format(req_json.get('userid')))

        # user must be signed in to update the profile description
        if request.session.get('{}'.format(user.user_id), False) is False:
            return JSONResponse.new(code=400, message='user id {} must be logged in'.format(user.user_id))

        new_desc = req_json.get('description', '')
        if len(new_desc) < 1 or len(new_desc) > 255:
            return JSONResponse.new(
                code=400,
                message='description doesn\'t meet the length requirements: {}'.format(
                    len(new_desc))
            )

        user.about = new_desc
        user.save(update_fields=['about'])
        return JSONResponse.new(code=200, message='success')


class UserEmail(View):
    """ Returns the users email address update the users email address
        POST: required json object {
            'userid': the user id of the user who will be updated,
            'email': the new email address
        }
        return object {
            'message': success or not
            'email': the updated email address
        }
    """

    def get(self, request: HttpRequest, user_id: str):
        try:
            user = Users.objects.get(user_id__exact=user_id)
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='user id {} was not found'.format(user_id))

        email = user.email
        return JSONResponse.new(code=200, message='success', email=email)

    def post(self, request: HttpRequest):
        try:
            req_json = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            return JSONResponse.new(code=400, message='json decode error, bad data sent to the server')

        try:
            user = Users.objects.get(user_id__exact=req_json.get('userid'))
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='user id {} was not found'.format(user_id))

        new_email = req_json.get('email', None)
        if new_email and len(new_email) < 255 and len(new_email) > 3:
            user.email = new_email
            user.save(update_fields=['email'])
            return JSONResponse.new(code=200, message='success', email=new_email)

        return JSONResponse.new(code=400, message='bad email', email=new_email)


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
            user = Users.objects.get(user_id__exact=req_json.get('userid'))
            follower = Users.objects.get(user_name__exact=req_json.get('username'))
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='userid {} or username {} not found'.format(req_json.get('userid'), req_json.get('username')))

        user.following.add(follower)
        follower.follower_count += 1
        follower.save()
        user.save()

        return JSONResponse.new(code=200,
                                message='success',
                                followcount=user.following.count(),
                                followname=follower.user_name,
                                followavatar=follower.profile_url)


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
            follower = user.following.get(
                user_name__exact=req_json.get('username'))
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='userid {} or username {} not found'.format(req_json['userid'], req_json['username']))

        follower.follower_count -= 1
        user.following.remove(follower)
        follower.save()
        user.save()
        return JSONResponse.new(code=200, message='success', followercount=user.following.count())


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

        # is there a better way?
        aws.remove_profile_image('{}.png'.format(user.user_name))
        url = aws.upload_profile_image('{}.png'.format(user.user_name), req_json.get('profilepic'))

        user.profile_url = url
        user.save(update_fields=['profile_url'])

        for post in user.posts_set.all():
            post.author_profile_url = url
            post.save()

        return JSONResponse.new(code=200, message='success', avatar=url)


class UserSearch(View):
    """ returns the username, avatar of the user if found.
        apiendpoint/<user> this can be the username or a user name.
        returned JSON object {
            'username': users username,
            'avatar': the url to the users avatar
        }
    """

    def get(self, request: HttpRequest, user_search: str):
        if ' ' in user_search:
            [first, *last] = user_search.split(' ')

            last_name = ''
            for name in last:
                last_name = ''.join([last_name, name, ' '])

            user = Users.objects.filter(first_name__icontains=first)
            if not user:
                user = Users.objects.filter(last_name__icontains=last_name)
                if not user:
                    return JSONResponse.new(code=400, message='Couldn\'t find any users using: {}'.format(user_search))
        else:
            # no space separated words, let's assume it's either a username or a first or last name
            user = Users.objects.filter(user_name__icontains=user_search)
            if not user:
                user = Users.objects.filter(first_name__icontains=user_search)
                if not user:
                    user = Users.objects.filter(last_name__icontains=user_search)
                    if not user:
                        return JSONResponse.new(code=400, message='Couldn\'t find any users using: {}'.format(user_search))

        found = []
        for found_user in user:
            found.append({
                'username': found_user.user_name,
                'avatar': found_user.profile_url
            })
        return JSONResponse.new(code=200, message='success', users=found)
