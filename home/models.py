from django.db import models

# Create your models here.

class UserProfile(models.Model):
    username = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    profile_pic = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    connections = models.TextField(blank=True)
    requests = models.TextField(blank=True)
    post_ids = models.TextField(blank=True)
    
    def __str__(self):
        return self.username
