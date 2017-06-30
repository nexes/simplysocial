""" handles authenticating a user, or creating/deleting a new user """
from user.models import Users
from secrets import token_hex
from random import random
import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, JsonResponse
from django.core.signing import Signer
from django.db import IntegrityError
from django.utils import timezone
from django.views import View



class AuthUserLogin(View):
    """ authenticate a users login request """

    def _verify_user_password(self, user: Users, pass_check: str)-> bool:
        signer = Signer(salt=user.salt_hash)
        user_pass_hash = user.password_hash
        challenge_hash = signer.signature(pass_check)

        return user_pass_hash == challenge_hash

    def post(self, request: HttpRequest):
        resp = JsonResponse({})

        try:
            request_json = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            resp.content = json.dumps({
                "message": "request decode error, bad data sent to the server"
                })
            resp.status_code = 400
            return resp

        try:
            user = Users.objects.get(user_name__exact=request_json.get('username'))
        except ObjectDoesNotExist:
            resp.status_code = 400
            resp.content = json.dumps({
                "message": "user {} is not found".format(request_json.get('username'))
            })
            return resp

        if self._verify_user_password(user, request_json.get('password')):
            user.last_login_date = timezone.now()
            request.session['user_id'] = user.user_id

            user.save()
        else:
            resp.status_code = 400
            resp.content = json.dumps({
                "message": "username {}, or password {} is incorrect".format(
                    request_json.get('username'),
                    request_json.get('password')
                )
            })
            return resp

        resp.status_code = 200
        resp.content = json.dumps({
            "message": "user is logged in",
            "user_id": user.user_id
        })
        return resp


class AuthUserCreate(View):
    """ create a new user """
    def check_required_inputs(self, items: [str]):
        """ check if each item passed is both not empty and the correct length,
            if one item doesn't meet the requirements the functions throws an error
        """
        for item in items:
            count = len(item)
            if count == 0 or count > 40:
                raise ValueError('Item doesn\'t meet length requirements.', item, count)


    def post(self, request: HttpRequest):
        resp = JsonResponse({})

        try:
            request_json = json.loads(request.body.decode('UTF-8'))
        except json.JSONDecodeError:
            resp.content = json.dumps({
                "message": "request decode error, bad data sent to the server"
                })
            resp.status_code = 400
            return resp

        #these are required keys
        _user_name = request_json.get('username')
        _last_name = request_json.get('lastname')
        _first_name = request_json.get('firstname')
        _password = request_json.get('password')

        try:
            self.check_required_inputs([
                _user_name,
                _first_name,
                _last_name,
                _user_name,
                _password
            ])
        except ValueError as err:
            resp.content = json.dumps({
                "message": "{}, len {}, incorrect size requirement".format(err.args[0], err.args[1])
                })
            resp.status_code = 400
            return resp

        try:
            Users.objects.get(user_name__exact=_user_name)
        except ObjectDoesNotExist:
            #GOOD, lets create a new user
            new_user = Users()
            salt = token_hex(16)
            signer = Signer(salt=salt)

            new_user.user_id = int(random() * 1000000)
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
                #hash, userID etc. re create them
                resp.content = json.dumps({"message":"username and email need to be unique"})
                resp.status_code = 500
                return resp

        else:
            resp.content = json.dumps({
                "message": "username {} is already taken".format(_user_name)
                })
            resp.status_code = 400
            return resp

        resp.content = json.dumps({
            "message": "user created successfully",
            "user_id": new_user.user_id
            })
        resp.status_code = 200
        return resp



class AuthUserDelete(View):
    """ authenticate a users delete request, make them type in their password """
    def _verify_user_password(self, user: Users, pass_check: str)-> bool:
        signer = Signer(salt=user.salt_hash)
        user_pass_hash = user.password_hash
        challenge_hash = signer.signature(pass_check)

        return user_pass_hash == challenge_hash

    def post(self, request: HttpRequest):
        resp = JsonResponse({})

        try:
            resp_json = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            resp.content = json.dumps({
                "message": "request decode error, bad data sent to the server"
                })
            resp.status_code = 400
            return resp

        try:
            user = Users.objects.get(user_name__exact=resp_json['username'])
        except ObjectDoesNotExist:
            resp.status_code = 400
            resp.content = json.dumps({
                "message": "user {} is not found".format(resp_json['username'])
            })
            return resp

        if self._verify_user_password(user, resp_json['password']):
            user.delete()
        else:
            resp.status_code = 400
            resp.content = json.dumps({
                "message": "username {}, or password {} is incorrect".format(
                    resp_json.get('username'),
                    resp_json.get('password')
                )
            })
            return resp

        resp.status_code = 200
        resp.content = json.dumps({
            "message": "user deleted",
            "user_id": user.user_id
        })
        return resp
