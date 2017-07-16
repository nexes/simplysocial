""" handles authenticating a user, or creating/deleting a new user """
from lifesnap.util import JSONResponse
from user.models import Users
from secrets import token_hex
from uuid import uuid4
import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.core.signing import Signer
from django.db import IntegrityError
from django.utils import timezone
from django.views import View



class AuthUserLogin(View):
    """ authenticate a users login request:
        method = POST: required json object {
            'username': 'the username',
            'password': 'the password'
        }
        sucessfull login will return the users_id, this is needed for other requestes.
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
            return JSONResponse.new(code=400, message='user {} is already sigend in'.format(request_json.get('username')))

        if self._verify_user_password(user, request_json.get('password')):
            user.last_login_date = timezone.now()
            request.session['{}'.format(user.user_id)] = True
            user.save()
        else:
            message = 'username {}, or password {} is incorrect'.format(
                request_json.get('username'),
                request_json.get('password'))
            return JSONResponse.new(code=400, message=message)

        return JSONResponse.new(code=200, message='success', userid=user.user_id)


class AuthUserLogoff(View):
    pass


class AuthUserCreate(View):
    """ create a new user
        method = POST: required json object {
            'username': 'the username <required: needs to be unique>',
            'password': 'the password <required>',
            'firstname': 'the first name <required>',
            'lastname': 'the last name <required>',
            'email': 'the email <optional>',
            'about': 'about text <optional>
        }
        sucessfull creation will return the user_id of the new user.
    """
    def check_required_inputs(self, items: [str]):
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

        #these are required keys
        _user_name = request_json.get('username')
        _first_name = request_json.get('firstname')
        _last_name = request_json.get('lastname')
        _password = request_json.get('password')

        try:
            self.check_required_inputs([
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
            #GOOD, lets create a new user
            new_user = Users()
            salt = token_hex(16)
            signer = Signer(salt=salt)

            new_user.user_id = uuid4().time_low
            new_user.first_name = _first_name
            new_user.last_name = _last_name
            new_user.user_name = _user_name
            new_user.salt_hash = salt
            new_user.password_hash = signer.signature(_password)
            new_user.email = request_json.get('email', '{}@noemail.set'.format(_user_name))
            new_user.about = request_json.get('about', '')
            new_user.last_login_date = timezone.now()

            try:
                new_user.save()
            except IntegrityError as err:
                #if this is because we have a collision with our random numbers
                #hash, userID etc. re-create them
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
            user.delete()
        else:
            return JSONResponse.new(code=400, message='username {}, or password {} is incorrect'.format(resp_json.get('username'), resp_json.get('password')))

        return JSONResponse.new(code=200, message='success', userid=user.user_id)
