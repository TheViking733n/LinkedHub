from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = 'LinkedHub Admin Panel'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('post/', include('post.urls')),
    path('', include('home.urls')),
]


# Added for vercel deployment
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)