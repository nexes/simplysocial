""" Users model """
from django.db import models


class Users(models.Model):
    """ Users table describing the user """

    class Meta:
        ordering = ['-user_name']

    user_id = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=40, blank=False)
    last_name = models.CharField(max_length=40, blank=False)
    user_name = models.CharField(max_length=40, unique=True, blank=False)
    password_hash = models.CharField(max_length=32, unique=True)
    salt_hash = models.CharField(max_length=32, unique=True)
    email = models.EmailField(unique=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_login_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    about = models.CharField(max_length=255, blank=True)
    profile_url = models.CharField(max_length=100, blank=True)
    follower_count = models.IntegerField(default=0)
    following = models.ManyToManyField('self', symmetrical=False)

    def __str__(self):
        return "{}, {}: {}".format(self.last_name, self.first_name, self.email)
