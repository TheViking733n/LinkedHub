from django.db import models

# Create your models here.

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    author_id = models.CharField(max_length=100)
    likes = models.IntegerField(default=0)
    comment_ids = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    content = models.TextField()
    author_id = models.CharField(max_length=100)
    likes = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content