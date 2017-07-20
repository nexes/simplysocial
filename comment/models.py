from django.db import models
from post.models import Posts


class Comments(models.Model):
    class Meta:
        ordering = ['-creation_date']

    comment_id = models.IntegerField(unique=True, blank=False)
    author_id = models.IntegerField(blank=False)
    creation_date = models.DateField(auto_now_add=True)
    message = models.CharField(max_length=255, blank=False)
    like_count = models.IntegerField(default=0)
    report_count = models.IntegerField(default=0)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return '{}: by {}'.format(self.comment_id, self.author_id)
