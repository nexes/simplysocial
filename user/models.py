""" Users model """
from django.db import models


class Users(models.Model):
    """ Users table describing the user """
    user_id = models.IntegerField()
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    user_name = models.CharField(max_length=40)
    password_hash = models.CharField(max_length=32)
    salt_hash = models.CharField(max_length=32)
    email = models.EmailField()
    creation_date = models.DateTimeField(auto_now_add=True)
    last_login_date = models.DateTimeField()
    is_active = models.BooleanField()
    about = models.CharField(max_length=100)
    # profile_pic
    # message_id = foriegn key
    # friends_id = many to many key

    def __str__(self):
        return "{}, {}: {}".format(self.last_name, self.first_name, self.email)
