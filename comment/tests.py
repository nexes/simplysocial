import json
from base64 import b64encode
from user.models import Users
from django.utils import timezone
from django.core.signing import Signer
from django.test import TestCase, Client, tag



@tag('usercomment')
class CreateComment(TestCase):
    def _login_user(self):
        url = '/snaplife/api/auth/user/login/'
        data = json.dumps({'username': self.user.user_name, 'password': 'password123'})
        resp = self.client.post(url, data, content_type='application/json')

        print('\tuser post: login status {}'.format(resp.status_code == 200))
        self.assertEqual(resp.status_code, 200)

    def _comment_count(self, commentid: str):
        count_url = '/snaplife/api/user/posts/comment/count/{}/'.format(commentid)

        resp = self.client.get(count_url)
        print('\tcomment_count count is now {}'.format(resp.json()['count']))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'success')

    def _comment_remove(self, commentid: str):
        remove_url = '/snaplife/api/user/posts/comment/delete/'

        data = json.dumps({
            'userid': self.user.user_id,
            'commentid': commentid
        })

        resp = self.client.post(remove_url, data, content_type='application/json')
        print('\tcomment_remove comment id {}'.format(resp.json()['commentid']))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'success')

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

    def test_create_comment(self):
        self._login_user()
        comment_url = '/snaplife/api/user/posts/comment/create/'
        post_url = '/snaplife/api/user/posts/create/'

        # create a new post
        with open('/Users/jberria/Pictures/test1sprites0.png', 'rb') as f:
            encode = b64encode(f.read())

        data = json.dumps({
            'image': encode.decode('utf-8'),
            'message': 'this is a description of our post',
            'title': 'a test title!!!',
            'userid': self.user.user_id
        })

        resp = self.client.post(post_url, data, content_type='application/json')
        return_json = resp.json()
        post_id = return_json['postid']

        print('\tcomment_create: creating new post for user: {}, postid {}'.format(
            resp.status_code, post_id))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'success')

        comment = json.dumps({
            'postid': post_id,
            'userid': self.user.user_id,
            'message': 'this is a comment to your post'
        })

        resp = self.client.post(comment_url, comment, content_type='application/json')
        return_json = resp.json()
        comment_id = return_json['commentid']

        print('\tcomment_create: comment created: {}'.format(comment_id))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'success')

        #check the comment count
        self._comment_count(post_id)
        self._comment_remove(comment_id)
        self._comment_count(post_id)
