import json
from django.test import TestCase, Client


class UserTestCase(TestCase):
    def _create_json_request(self, data: json):
        resp = self.client.post('/snaplife/api/auth/user/create/',
                                json.dumps(data),
                                content_type='application/json')

        return resp

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_good_new_user(self):
        """ make sure a new user is created when the correct data is passed """
        resp = self._create_json_request({
            'username': 'mmouse',
            'firstname': 'mickey',
            'lastname': 'mouse',
            'email': 'mmouse@disney.com',
            'password': 'topsecret123'
        })

        print('good_new_user: status_code = {}: {}'.format(resp.status_code, resp.json()['message']))
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

        print('bad_new_user: status_code = {}: {}'.format(resp.status_code, resp.json()['message']))
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

        print('dup_new_user: status_code = {}: {}'.format(resp.status_code, resp.json()['message']))
        self.assertNotEqual(resp.status_code, 200)
        self.assertContains(resp, 'username mmouse is already taken', status_code=400)
