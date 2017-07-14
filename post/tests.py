from urllib.parse import quote
from datetime import datetime
from base64 import b64encode
import json

from user.models import Users
from django.utils import timezone
from django.test import TestCase, tag, Client
from django.core.signing import Signer



@tag('userpost')
class UserPostCreate(TestCase):
    def _login_user(self, password: str):
        url = '/snaplife/api/auth/user/login/'
        data = json.dumps({'username': self.user.user_name, 'password': password})
        resp = self.client.post(url, data, content_type='application/json')

        print('\tuser post: login status {}'.format(resp.status_code == 200))
        self.assertEqual(resp.status_code, 200)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        salt = 'blahfffffj349feiblah123'
        signer = Signer(salt=salt)

        user = Users()
        user.user_id = 324
        user.first_name = 'Billy'
        user.last_name = 'Bobtest'
        user.user_name = 'myUsername'
        user.last_login_date = timezone.now()
        user.password_hash = signer.signature('password123')
        user.salt_hash = salt
        user.save()

        cls.user = user
        cls.client = Client()

    # def test_post_create(self):
    #     self._login_user('password123')

    #     url = '/snaplife/api/user/posts/create/'
    #     url2 = '/snaplife/api/user/count/{}/posts/'.format(self.user.user_id)

    #     with open('/Users/jberria/Pictures/test1sprites0.png', 'rb') as f:
    #         encode = b64encode(f.read())

    #     data = json.dumps({
    #         'image': encode.decode('utf-8'),
    #         'message': 'this is a description of our post',
    #         'title': 'a test title!!!',
    #         'userid': self.user.user_id
    #     })

    #     resp = self.client.post(url, data, content_type='application/json')
    #     print('\tpost_create: creating new post for user: {}, postid {}'.format(resp.status_code, resp.json()['postid']))
    #     self.assertEqual(resp.status_code, 200)
    #     self.assertContains(resp, 'success')

    #     resp2 = self.client.get(url2)
    #     print('\tpost_create: checking post count for user: count = {}'.format(resp2.json()['count']))
    #     self.assertEqual(resp2.status_code, 200)
    #     self.assertContains(resp2, 'count')

    # def test_post_without_signin(self):
    #     url = '/snaplife/api/user/posts/create/'
    #     url2 = '/snaplife/api/user/count/{}/posts/'.format(self.user.user_id)
    #     data = json.dumps({
    #         'image': 'not testable from here',
    #         'message': 'This will be apart of the the image post',
    #         'userid': self.user.user_id
    #     })

    #     resp = self.client.post(url, data, content_type='application/json')
    #     print('\tpost_create: creating new post without signing in: {}'.format(resp.status_code))
    #     self.assertEqual(resp.status_code, 400)
    #     self.assertContains(resp, 'user is not signed in', status_code=400)

    #     resp2 = self.client.get(url2)
    #     print('\tpost_create: checking post count for user not signed in: count = {}'.format(resp2.json()['count']))
    #     self.assertEqual(resp2.status_code, 200)
    #     self.assertContains(resp2, 'count')

    # def test_post_delete(self):
    #     url_delete = '/snaplife/api/user/posts/delete/'
    #     url_create = '/snaplife/api/user/posts/create/'
    #     self._login_user('password123')

    #     with open('/Users/jberria/Pictures/test1sprites0.png', 'rb') as f:
    #         encode = b64encode(f.read())

    #     create_data = json.dumps({
    #         'image': encode.decode('utf-8'),
    #         'message': 'this is a description of our post, a test post message',
    #         'title': 'a test title!!!',
    #         'userid': self.user.user_id
    #     })
    #     resp = self.client.post(url_create, create_data, content_type='application/json')
    #     print('\tpost_delete: creating new post signing in: {}'.format(resp.status_code))

    #     delete_data = json.dumps({
    #         'userid': self.user.user_id,
    #         'title': 'a test title!!!'
    #     })
    #     resp2 = self.client.post(url_delete, delete_data, content_type='application/json')
    #     print('\tpost_delete: deleting new post: {}, {}'.format(resp2.status_code, resp2.json()['message']))

    #     self.assertEqual(resp2.status_code, 200)
    #     self.assertContains(resp2, 'success')

    # def test_post_search(self):
    #     self._login_user('password123')
    #     q_str = quote('test title')
    #     now = datetime(2017, 7, 1)

    #     url = '/snaplife/api/user/posts/create/'
    #     title_search = '/snaplife/api/user/posts/search/title/{}/{}/3/'.format(self.user.user_id, q_str)
    #     date_search = '/snaplife/api/user/posts/search/range/{}/{}/3/'.format(self.user.user_id, int(now.timestamp()))

    #     with open('/Users/jberria/Pictures/test1sprites0.png', 'rb') as f:
    #         encode = b64encode(f.read())

    #     data = json.dumps({
    #         'image': encode.decode('utf-8'),
    #         'message': 'this is a description of our post',
    #         'title': 'a test title!!!',
    #         'userid': self.user.user_id
    #     })
    #     data1 = json.dumps({
    #         'image': encode.decode('utf-8'),
    #         'message': 'this is another post, the second one',
    #         'title': 'test title!!!',
    #         'userid': self.user.user_id
    #     })
    #     data2 = json.dumps({
    #         'image': encode.decode('utf-8'),
    #         'message': 'django python post about this, i dont know',
    #         'title': 'a test',
    #         'userid': self.user.user_id
    #     })
    #     self.client.post(url, data, content_type='application/json')
    #     self.client.post(url, data1, content_type='application/json')
    #     self.client.post(url, data2, content_type='application/json')

    #     resp = self.client.get(title_search)
    #     self.assertEqual(resp.status_code, 200)
    #     self.assertContains(resp, 'success')

    #     resp = self.client.get(date_search)
    #     self.assertEqual(resp.status_code, 200)
    #     self.assertContains(resp, 'success')

    def test_post_update(self):
        self._login_user('password123')
        url_update = '/snaplife/api/user/posts/update/'
        url_create = '/snaplife/api/user/posts/create/'

        with open('/Users/jberria/Pictures/test1sprites0.png', 'rb') as f:
            encode = b64encode(f.read())

        data = json.dumps({
            'image': encode.decode('utf-8'),
            'message': 'this is a description of our post',
            'title': 'a test title!!!',
            'userid': self.user.user_id
        })
        resp = self.client.post(url_create, data, content_type='application/json')

        updated_data = json.dumps({
            'userid': self.user.user_id,
            'postid': resp.json()['postid'],
            'title': 'This is a new and improved title',
            'message': 'this is a new and impoved message for the postAAAAAAAA!!!!!'
        })
        resp = self.client.post(url_update, updated_data, content_type='application/json')

        print('\tnew title: {}'.format(resp.json()['post']['title']))
        print('\tnew message: {}'.format(resp.json()['post']['message']))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'success')
