""" handles authenticating a user, or creating/deleting a new user """
import json
from uuid import uuid4
from secrets import token_hex
from user.models import Users
from lifesnap.aws import AWS
from lifesnap.util import JSONResponse

from django.views import View
from django.utils import timezone
from django.http import HttpRequest
from django.db import IntegrityError
from django.core.signing import Signer
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie


class EnsureCSRFToken(View):
    """ Since this is an API endpoint only backend, we are not rendering any templates, no HTML is being returned
        Because of this, if the client doesn't already have our csrftoken set in their cookie they will receive a
        403 on all requests. Calling this GET endpoint before any other (only once is needed) will ensure to set the
        csrf token which is needed in the header of all requests for security.
    """
    @method_decorator(ensure_csrf_cookie)
    def get(self, request: HttpRequest):
        return JSONResponse.new(code=200, message='success')


class AuthUserLogin(View):
    """ authenticate a users login request:
        method = POST: required json object {
            'username': 'the username',
            'password': 'the password'
        }
        returned json object {
            'userid': the userid of the now logged in user
        }
    """

    def _verify_user_password(self, user: Users, pass_check: str)-> bool:
        signer = Signer(salt=user.salt_hash)
        user_pass_hash = user.password_hash
        challenge_hash = signer.signature(pass_check)

        return user_pass_hash == challenge_hash

    def post(self, request: HttpRequest):
        try:
            request_json = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            return JSONResponse.new(code=400, message='request decode error, bad data sent to the server')

        try:
            user = Users.objects.get(user_name__exact=request_json.get('username'))
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='user {} is not found'.format(request_json.get('username')))

        if request.session.get('{}'.format(user.user_id), False) is True:
            return JSONResponse.new(code=400, message='user {} is already signed in'.format(request_json.get('username')))

        if self._verify_user_password(user, request_json.get('password')):
            user.last_login_date = timezone.now()
            user.is_active = True
            request.session['{}'.format(user.user_id)] = True
            user.save()
        else:
            message = 'username {}, or password {} is incorrect'.format(
                request_json.get('username'),
                request_json.get('password'))
            return JSONResponse.new(code=403, message=message)

        return JSONResponse.new(code=200, message='success', userid=user.user_id)


class AuthUserLogoff(View):
    """ user log off
        method = POST: required json object {
            'userid': the users unique user id
        }
        returned json object {
            'userid': the user id of the now logged off user
        }
    """
    def post(self, request: HttpRequest):
        try:
            request_json = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            return JSONResponse.new(code=400, message='request decode error, bad data sent to the server')

        try:
            user = Users.objects.get(user_id__exact=request_json.get('userid'))
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='user {} is not found'.format(request_json.get('userid')))

        user.is_active = False
        user.save()
        del request.session['{}'.format(user.user_id)]
        return JSONResponse.new(code=200, message='success', userid=user.user_id)


class AuthUserCreate(View):
    """ create a new user
        method = POST: required json object {
            'username': 'the username <required: needs to be unique>',
            'password': 'the password <required>',
            'firstname': 'the first name <required>',
            'lastname': 'the last name <required>',
            'email': 'the email <optional>',
            'about': 'about text <optional>,
            'profilepic': base64 encode picture for the profile pic <optional>
        }
        sucessfull creation will return the user_id of the new user.
    """
    def _check_required_inputs(self, items: [str]):
        """ check if each item passed is both not empty and the correct length """
        for item in items:
            count = len(item)
            if count == 0 or count > 40:
                raise ValueError('Item doesn\'t meet length requirements.', item, count)

    def post(self, request: HttpRequest):
        try:
            request_json = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            return JSONResponse.new(code=400, message='request decode error, bad data sent to the server')

        # these are required keys
        _user_name = request_json.get('username')
        _first_name = request_json.get('firstname')
        _last_name = request_json.get('lastname')
        _password = request_json.get('password')

        try:
            self._check_required_inputs([
                _user_name,
                _first_name,
                _last_name,
                _password
            ])
        except ValueError as err:
            return JSONResponse.new(code=400, message='{}, len {}, incorrect size requirement'.format(err.args[0], err.args[1]))

        try:
            Users.objects.get(user_name__exact=_user_name)
        except ObjectDoesNotExist:
            # GOOD, lets create a new user
            new_user = Users()
            salt = token_hex(16)
            signer = Signer(salt=salt)

            new_user.user_id = uuid4().time_mid
            new_user.first_name = _first_name
            new_user.last_name = _last_name
            new_user.user_name = _user_name
            new_user.salt_hash = salt
            new_user.password_hash = signer.signature(_password)
            new_user.email = request_json.get('email', '{}@noemail.set'.format(_user_name))
            new_user.about = request_json.get('about', '')
            new_user.last_login_date = timezone.now()

            if request_json.get('profilepic') is not None:
                aws = AWS('snap-life')
                key_name = '{}.png'.format(request_json.get('profilepic'))
                url = aws.upload_profile_image(new_user.user_name, key_name)

                new_user.profile_url = url

            try:
                new_user.save()
            except IntegrityError as err:
                # if this is because we have a collision with our random numbers
                # hash, userID etc. re-create them
                return JSONResponse.new(code=500, message='username and email need to be unique')

        else:
            return JSONResponse.new(code=400, message='username {} is already taken'.format(_user_name))

        return JSONResponse.new(code=200, message='success', userid=new_user.user_id)



class AuthUserDelete(View):
    """ authenticate a users delete request, make them type in their password
        method = POST: required json object {
            'username': 'the username',
            'password': 'the password'
        }
        sucessfull deletion will return the user_id of the removed user.
    """
    def _verify_user_password(self, user: Users, pass_check: str)-> bool:
        signer = Signer(salt=user.salt_hash)
        user_pass_hash = user.password_hash
        challenge_hash = signer.signature(pass_check)

        return user_pass_hash == challenge_hash

    def post(self, request: HttpRequest):
        aws = AWS('snap-life')

        try:
            resp_json = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JSONResponse.new(code=400, message='request decode error, bad data sent to the server')

        try:
            user = Users.objects.get(user_name__exact=resp_json.get('username'))
        except ObjectDoesNotExist:
            return JSONResponse.new(code=400, message='user {} is not found'.format(resp_json['username']))

        if self._verify_user_password(user, resp_json.get('password')):
            try:
                del request.session['{}'.format(user.user_id)]
            except KeyError:
                pass

            all_post = user.posts_set.all()
            post_key_names = []
            for post in all_post:
                post_key_names.append(post.image_name)

            aws.remove_images(post_key_names)
            aws.remove_profile_image(user.user_name)
            user.delete()
        else:
            return JSONResponse.new(code=400, message='username {}, or password {} is incorrect'.format(resp_json.get('username'), resp_json.get('password')))

        return JSONResponse.new(code=200, message='success', userid=user.user_id)
