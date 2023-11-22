from django.urls import path, include
from home import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signup', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('login', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('logout', views.logout, name='logout'),
    path('settings/', views.settings, name='settings'),
    path('settings', views.settings, name='settings'),
    path('connect_request/', views.connect_request, name='connect_request'),
    path('connect_request', views.connect_request, name='connect_request'),
    path('connect_accept/', views.connect_accept, name='connect_accept'),
    path('connect_accept', views.connect_accept, name='connect_accept'),
    path('cancel_request/', views.cancel_request, name='cancel_request'),
    path('cancel_request', views.cancel_request, name='cancel_request'),
    path('connect_reject/', views.connect_reject, name='connect_reject'),
    path('connect_reject', views.connect_reject, name='connect_reject'),
    path('connect_remove/', views.connect_remove, name='connect_remove'),
    path('connect_remove', views.connect_remove, name='connect_remove'),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>', views.profile, name='profile'),
]
