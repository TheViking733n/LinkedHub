from django.db import models

# Create your models here.

class UserProfile(models.Model):
    username = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    profile_pic = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    organization = models.CharField(max_length=100, blank=True)
    is_organization = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username


class Connection(models.Model):
    user1 = models.CharField(max_length=100)
    user2 = models.CharField(max_length=100)
    
    def __str__(self):
        return self.user1 + ' - ' + self.user2


class PendingRequest(models.Model):
    sender = models.CharField(max_length=100)
    receiver = models.CharField(max_length=100)
    
    def __str__(self):
        return self.sender + ' - ' + self.receiver
