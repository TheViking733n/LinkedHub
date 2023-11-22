from django.urls import path, include
from post import views

urlpatterns = [
    path('create/', views.create_post, name='create_post'),
    path('create', views.create_post, name='create_post'),
    path('like/', views.like_item, name='like_item'),
    path('like', views.like_item, name='like_item'),
    path('comment/', views.comment_post, name='comment_post'),
    path('comment', views.comment_post, name='comment_post'),
    path('delete/', views.delete_item, name='delete_item'),
    path('delete', views.delete_item, name='delete_item'),
    path('<int:post_id>/', views.view_post, name='view_post'),
    path('<int:post_id>', views.view_post, name='view_post'),
]
