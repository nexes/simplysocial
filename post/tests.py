from user.models import Users
from post.models import Posts
import json

from django.utils import timezone
from django.test import TestCase, tag, Client
from django.core.signing import Signer



@tag('userpost')
class UserPostCreate(TestCase):
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

    def _login_user(self, user: Users, password: str):
        url = '/snaplife/api/auth/user/login/'
        data = json.dumps({'username': user.user_name, 'password': password})
        resp = self.client.post(url, data, content_type='application/json')

        print('\tuser post: login status {}'.format(resp.status_code == 200))
        self.assertEqual(resp.status_code, 200)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_post_create(self):
        user = self._create_user('joe', 'password123')
        self._login_user(user, 'password123')

        url = '/snaplife/api/user/posts/create/'
        url2 = '/snaplife/api/user/count/{}/posts/'.format(user.user_id)
        data = json.dumps({
            'image': 'not testable from here',
            'message': 'This will be apart of the the image post',
            'userid': user.user_id
        })

        resp = self.client.post(url, data, content_type='application/json')
        print('\tpost_create: creating new post for user: {}'.format(resp.status_code))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'success')

        resp2 = self.client.get(url2)
        print('\tpost_create: checking post count for user: count = {}'.format(resp2.json()['count']))
        self.assertEqual(resp2.status_code, 200)
        self.assertContains(resp2, 'count')

    def test_post_without_signin(self):
        user = self._create_user('joe', 'password123')

        url = '/snaplife/api/user/posts/create/'
        url2 = '/snaplife/api/user/count/{}/posts/'.format(user.user_id)
        data = json.dumps({
            'image': 'not testable from here',
            'message': 'This will be apart of the the image post',
            'userid': user.user_id
        })

        resp = self.client.post(url, data, content_type='application/json')
        print('\tpost_create: creating new post without signing in: {}'.format(resp.status_code))
        self.assertEqual(resp.status_code, 400)
        self.assertContains(resp, 'user is not signed in', status_code=400)

        resp2 = self.client.get(url2)
        print('\tpost_create: checking post count for user not signed in: count = {}'.format(resp2.json()['count']))
        self.assertEqual(resp2.status_code, 200)
        self.assertContains(resp2, 'count')
