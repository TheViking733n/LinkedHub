from django.db import models

# Create your models here.

class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    author_id = models.CharField(max_length=100)
    # likes = models.IntegerField(default=0)
    # comment_ids = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    content = models.TextField()
    author_id = models.CharField(max_length=100)
    # likes = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content


class Like(models.Model):
    item_id = models.IntegerField()
    item_type = models.CharField(max_length=10)  # 'post' or 'comment'
    user_id = models.CharField(max_length=100)   # username of the liker
    
    def __str__(self):
        return self.item_type + ' ' + str(self.item_id) + ' liked by ' + self.user_id

