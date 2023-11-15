from django.contrib import admin
from .models import UserProfile, Connection, PendingRequest
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Connection)
admin.site.register(PendingRequest)