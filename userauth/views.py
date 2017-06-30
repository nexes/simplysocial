""" handles authenticating a user, or creating/deleting a new user """
from user.models import Users
from secrets import token_hex
from datetime import datetime
from random import random
import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, JsonResponse
from django.core.signing import Signer
from django.db import IntegrityError
from django.views import View


class AuthUserLogin(View):
    """ authenticate a users login request """
    def post(self, request: HttpRequest):
        pass


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
            resp.content = json.dumps({"message": "request decode error, bad data sent to the server"})
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
            new_user.last_login_date = datetime.now()

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
    """ authenticate a users delete request """
    def post(self, request: HttpRequest):
        pass
