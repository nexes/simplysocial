import json

from user.models import Users
from post.models import Posts
from django.utils import timezone
from django.core.signing import Signer
from django.test import TestCase, Client, tag


@tag('usertest')
class UserCountTest(TestCase):
    """ make sure we can count the number of post and followers of a user """
    def _create_request(self, user_id: int, count_type: str):
        resp = self.client.get('/snaplife/api/user/count/{}/{}/'.format(user_id, count_type))
        return resp

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

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_user_count(self):
        """ test the user's follower and post counts """
        user = self._create_user('mMouse', 'password2345')
        post = Posts()
        post.post_id = 123
        post.image_name = '234234'
        post.image_url = 'something.com'
        post.message = 'some post message'
        post.view_count = 23
        post.like_count = 56
        post.save()

        post2 = Posts()
        post2.post_id = 122343
        post.image_name = '23sfsdf4234'
        post2.image_url = 'somethingelse.com'
        post2.message = 'some post message again'
        post2.view_count = 233
        post2.like_count = 5634
        post2.save()

        user.posts_set.add(post)
        user.posts_set.add(post2)
        resp = self._create_request(user.user_id, 'posts')

        print('\tuser_count status_code: {}, post count: {}'.format(resp.status_code, resp.json()['count']))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'count')

    def test_no_user_count(self):
        """ make sure the correct error comes back if an incorrect user_id is requested """
        resp = self._create_request(12389, 'posts')

        print('\tno_user_count: {}: {}'.format(resp.status_code, resp.json()['message']))
        self.assertEqual(resp.status_code, 400)
        self.assertContains(resp, 'bad user id', status_code=400)


@tag('usertest')
class UserDescriptionTest(TestCase):
    def _create_request(self, user_id: int, data: json = None):
        if data is None:
            resp = self.client.get('/snaplife/api/user/description/{}/'.format(user_id))
        else:
            resp = self.client.post('/snaplife/api/user/description/', data=json.dumps(data), content_type='application/json')
        return resp

    def _create_user(self, username: str, password: str):
        salt = 'blahfffffj349feiblah123'
        signer = Signer(salt=salt)

        user = Users()
        user.user_id = 324
        user.first_name = 'Billy'
        user.last_name = 'Bobtest'
        user.user_name = username
        user.about = "This is about me and the things I like"
        user.last_login_date = timezone.now()
        user.password_hash = signer.signature(password)
        user.salt_hash = salt
        user.save()

        return user

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_get_description(self):
        user = self._create_user('mMouse', 'password123')
        resp = self._create_request(user.user_id)

        print('\tget_description: {}: {}'.format(resp.status_code, resp.json()['message']))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'This is about me')

    def test_set_description(self):
        user = self._create_user('mMouse', 'password1234567')
        resp = self._create_request(user.user_id, {
            'userid': user.user_id,
            'description': 'This is a new description set by me!!!!!!! :)'
        })

        print('\tset_description: {}: {}'.format(resp.status_code, resp.json()['message']))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'success')

    def test_set_long_description(self):
        user = self._create_user('mMouse', 'password1234567')
        resp = self._create_request(user.user_id, {
            'userid': user.user_id,
            'description': 'This is a new description set by me!!!!!!! :)AAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        })

        print('\tset_long_description: {}: {}'.format(resp.status_code, resp.json()['message']))
        self.assertEqual(resp.status_code, 400)
        self.assertContains(resp, 'length requirements', status_code=400)

@tag('usertest')
class UserFollowers(TestCase):
    def _login_user(self, username: str, password: str):
        url = '/snaplife/api/auth/user/login/'
        data = json.dumps({'username': username, 'password': password})
        resp = self.client.post(url, data, content_type='application/json')

        print('\tuser post: login status {}'.format(resp.status_code == 200))
        self.assertEqual(resp.status_code, 200)

    def _create_user(self, username: str, password: str, userid: int):
        salt = 'blahfffff{}j349'.format(password)
        signer = Signer(salt=salt)

        user = Users()
        user.user_id = userid
        user.first_name = 'Billy'
        user.last_name = 'Bobtest'
        user.user_name = username
        user.email = '{}@gmail.com'.format(username)
        user.about = "This is about me and the things I like"
        user.last_login_date = timezone.now()
        user.password_hash = signer.signature(password)
        user.salt_hash = salt
        user.save()

        return user

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_followers(self):
        url_new = '/snaplife/api/user/follow/new/'
        url_remove = '/snaplife/api/user/follow/remove/'

        jim = self._create_user('jimjim', 'password123', 123)
        jane = self._create_user('jjane', '123455', 344)
        sue = self._create_user('sueB', 'pass567word', 564)

        self._login_user(jim.user_name, 'password123')

        self.client.post(url_new, json.dumps({'userid': jim.user_id, 'username':jane.user_name}), content_type='application/json')
        resp = self.client.post(url_new, json.dumps({'userid': jim.user_id, 'username':sue.user_name}), content_type='application/json')

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['followercount'], 2)
        print('\ttest_followers: added two followers {}'.format(resp.json()['followercount']))

        resp = self.client.post(url_remove, json.dumps({'userid':jim.user_id, 'username':sue.user_name}), content_type='application/json')

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['followercount'], 1)
        print('\ttest_followers: removed one follower {}'.format(resp.json()['followercount']))


@tag('usertest')
class UserSearch(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def _create_user(self, username: str, password: str, userid: int):
        salt = 'blahfffff{}j349'.format(password)
        signer = Signer(salt=salt)

        user = Users()
        user.user_id = userid
        user.first_name = 'Billy'
        user.last_name = 'Bobtest'
        user.user_name = username
        user.email = '{}@gmail.com'.format(username)
        user.about = "This is about me and the things I like"
        user.last_login_date = timezone.now()
        user.password_hash = signer.signature(password)
        user.salt_hash = salt
        user.save()

        return user

    def test_search(self):
        url = '/snaplife/api/user/search/user/'

        jim = self._create_user('jim', 'txot', 1)
        john = self._create_user('jim-jam', 'txot1', 2)
        sally = self._create_user('sallbean', 'txot89', 3)

        print('testing username search')
        username_resp = self.client.get('{}{}/'.format(url, jim.user_name))

        self.assertEqual(username_resp.status_code, 200)
        self.assertEqual(len(username_resp.json()['users']), 2)
        print('{} users found'.format(len(username_resp.json()['users'])))

        print('testing last name search')
        lastname_resp = self.client.get('{}{}/'.format(url, sally.last_name))

        self.assertEqual(lastname_resp.status_code, 200)
        self.assertEqual(len(lastname_resp.json()['users']), 3)
        print('{} users found'.format(len(lastname_resp.json()['users'])))
