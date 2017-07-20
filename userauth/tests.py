import json
from base64 import b64encode
from user.models import Users

from django.test import TestCase, Client, tag
from django.core.signing import Signer
from django.utils import timezone


@tag('userauth')
class LoginUserTestCase(TestCase):
    def _create_user(self, username: str, password: str):
        salt = 'blahfffffj349feiblah123'
        signer = Signer(salt=salt)

        user = Users()
        user.user_id = 324
        user.first_name = 'Billy'
        user.last_name = 'Bobtest'
        user.user_name = username
        user.last_login_date = timezone.now()
        user.password_hash = signer.signature(password)
        user.salt_hash = salt
        user.save()

        return user

    def _create_json_request(self, data: json):
        resp = self.client.post(
            '/snaplife/api/auth/user/login/',
            json.dumps(data),
            content_type='application/json'
        )
        return resp

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_login_user(self):
        """ make sure login works with the correct username/password """
        self._create_user('bbobby', 'password123')
        resp = self._create_json_request({'username':'bbobby', 'password':'password123'})

        print('\tlogin_user status_code = {}: {}'.format(resp.status_code, resp.json()['message']))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'success', status_code=200)

    def test_login_bad_user(self):
        """ make sure login fails when a wrong username was given """
        self._create_user('jMorison', 'password123')
        resp = self._create_json_request({'username': 'jmorison', 'password': 'password123'})

        print('\tlogin_bad_user status_code = {}: {}'.format(resp.status_code, resp.json()['message']))
        self.assertEqual(resp.status_code, 400)
        self.assertContains(resp, 'is not found', status_code=400)

    def test_login_bad_password(self):
        """ make sure login fails when a wrong password is given """
        self._create_user('sallyD', 'leetDjango1234')
        resp = self._create_json_request({'username': 'sallyD', 'password': 'wrongPass123'})

        print('\tlogin_bad_password status_code = {}: {}'.format(resp.status_code, resp.json()['message']))
        self.assertEqual(resp.status_code, 400)
        self.assertContains(resp, 'is incorrect', status_code=400)


@tag('userauth')
class CreateUserTestCase(TestCase):
    def _create_json_request(self, data: json):
        resp = self.client.post(
            '/snaplife/api/auth/user/create/',
            json.dumps(data),
            content_type='application/json'
        )
        return resp

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_good_new_user(self):
        """ make sure a new user is created when the correct data is passed """

        with open('/Users/jberria/Pictures/test1sprites0.png', 'rb') as f:
            encode = b64encode(f.read())

        resp = self._create_json_request({
            'username': 'mmouse',
            'firstname': 'mickey',
            'lastname': 'mouse',
            'email': 'mmouse@disney.com',
            'password': 'topsecret123',
            'profilepic': encode.decode('UTF-8')
        })

        print('\tgood_new_user: status_code = {}: {}'.format(resp.status_code, resp.json()['message']))
        self.assertEqual(resp.status_code, 200)

    def test_bad_new_user(self):
        """ make sure a new user is not created when some data is missing """
        resp = self._create_json_request({
            'username': '',
            'firstname': 'mickey',
            'lastname': 'mouse',
            'email': 'mmouse@disney.com',
            'password': 'topsecret123'
        })

        print('\tbad_new_user: status_code = {}: {}'.format(resp.status_code, resp.json()['message']))
        self.assertNotEqual(resp.status_code, 200)
        self.assertContains(resp, 'incorrect size requirement', status_code=400)

    def test_duplicate_user_add(self):
        """ make sure a user with a duplicate username is not created """
        resp = self._create_json_request({
            'username': 'mmouse',
            'firstname': 'mickey',
            'lastname': 'mouse',
            'email': 'mmouse@disney.com',
            'password': 'topsecret123'
        })

        resp = self._create_json_request({
            'username': 'mmouse',
            'firstname': 'mickey',
            'lastname': 'mouse',
            'email': 'differentEmail@disney.com',
            'password': 'topsecret123'
        })

        print('\tdup_new_user: status_code = {}: {}'.format(resp.status_code, resp.json()['message']))
        self.assertNotEqual(resp.status_code, 200)
        self.assertContains(resp, 'username mmouse is already taken', status_code=400)


@tag('userauth')
class DeleteUserTestCase(TestCase):
    def _create_user(self, username: str, password: str):
        salt = 'blahj3245fj349feiblah123'
        signer = Signer(salt=salt)

        user = Users()
        user.user_id = 324
        user.first_name = 'Billy'
        user.last_name = 'Bob test'
        user.user_name = username
        user.last_login_date = timezone.now()
        user.password_hash = signer.signature(password)
        user.salt_hash = salt
        user.save()

        return user

    def _create_json_request(self, data: json):
        resp = self.client.post(
            '/snaplife/api/auth/user/delete/',
            json.dumps(data),
            content_type='application/json'
        )
        return resp

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_delete_user(self):
        """ make sure a user is deleted when the username and password is correct """
        self._create_user('tTester', 'password123')
        resp = self._create_json_request({'username': 'tTester', 'password':'password123'})

        print('\tdelete_user: status_code = {}: {}'.format(resp.status_code, resp.json()['message']))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'success', status_code=200)

    def test_delete_wrong_password(self):
        """ make sure nothing is deleted when wrong password is given """
        self._create_user('tTester', 'password123')
        resp = self._create_json_request({'username': 'tTester', 'password':'wrongPass123'})

        print('\tdelete_wrong_password: status_code = {}: {}'.format(resp.status_code, resp.json()['message']))
        self.assertEqual(resp.status_code, 400)
        self.assertContains(resp, 'is incorrect', status_code=400)

    def test_delete_wrong_username(self):
        """ make sure nothing is deleted when wrong username is given """
        self._create_user('tTester', 'password123')
        resp = self._create_json_request({'username': 'sBradly', 'password':'password123'})

        print('\tdelete_wrong_username: status_code = {}: {}'.format(resp.status_code, resp.json()['message']))
        self.assertEqual(resp.status_code, 400)
        self.assertContains(resp, 'is not found', status_code=400)
