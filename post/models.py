""" Posts Model """
from user.models import Users
from django.db import models


class Posts(models.Model):
    class Meta:
        ordering = ['-creation_date']

    post_id = models.IntegerField(blank=False, unique=True)
    image_url = models.CharField(blank=True, max_length=100)
    image_name = models.CharField(blank=True, max_length=100)
    message = models.CharField(max_length=254)
    message_title = models.CharField(blank=True, max_length=100)
    creation_date = models.DateTimeField(auto_now_add=True)
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    report_count = models.IntegerField(default=0)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return '{}: {}'.format(self.post_id, self.image_url)
