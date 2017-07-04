""" Posts Model """
from user.models import Users
from django.db import models


class Posts(models.Model):
    post_id = models.IntegerField(blank=False, unique=True)
    image_url = models.CharField(blank=False, unique=True, max_length=100)
    message = models.CharField(blank=True, max_length=254)
    creation_date = models.DateTimeField(auto_now_add=True)
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    report_count = models.IntegerField(default=0)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return 'something'
