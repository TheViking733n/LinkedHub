from django.urls import path, include
from post import views

urlpatterns = [
    path('create/', views.create_post, name='create_post'),
    path('like/', views.like_post, name='like_post'),
    path('comment/', views.comment_post, name='comment_post'),
    path('<int:post_id>/', views.view_post, name='view_post'),
]
