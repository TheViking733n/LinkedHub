from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from home.models import UserProfile
from post.models import Post

# Create your views here.

def home(request):
    return render(request, 'index.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        name = request.POST['name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        messages = []
        if len(username) < 3:
            messages.append('Username must be at least 3 characters long.')
        if password1 != password2:
            messages.append('Passwords do not match.')
        if username in User.objects.all().values_list('username', flat=True):
            messages.append('Username already exists.')
        if email in User.objects.all().values_list('email', flat=True):
            messages.append('Email already exists.')
        
        if len(messages) > 0:
            return render(request, 'signup.html', {'messages': messages})
        
        user = User.objects.create_user(first_name=name, username=username, email=email, password=password1)
        user_profile = UserProfile.objects.create(name=name, username=username)

        user.save()
        return redirect('login')
    
    return render(request, 'signup.html')


def login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'message': 'Invalid credentials.'})
    
    return render(request, 'login.html')


def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('home')


def profile(request, username):
    prof = UserProfile.objects.raw(f'SELECT * FROM home_userprofile WHERE username = "{username}"')[0]
    posts = Post.objects.raw(f'SELECT * FROM post_post WHERE author_id = "{username}" ORDER BY timestamp DESC')
    # connections = prof.connections.split(',')
    context = {
        'profile': prof,
        'posts': posts,
        # 'connections': connections,
    }
    if request.user.is_authenticated and request.user.username != username:
        mutual_connections = UserProfile.objects.raw(f'SELECT * FROM home_userprofile WHERE username = "{request.user.username}"')[0].connections.split(',')
        context['mutual_connections'] = mutual_connections

    return render(request, 'profile.html', context)

@login_required
def settings(request):
    prof = UserProfile.objects.raw(f'SELECT * FROM home_userprofile WHERE username = "{request.user.username}"')[0]
    
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        bio = request.POST['bio']
        image_base64 = request.POST['image_base64']
        if request.user.email != email:
            if email in User.objects.all().values_list('email', flat=True):
                context = {
                    'profile': prof,
                    'message': 'Error: Email already exists.',
                    'status': 'warning'
                }
                return render(request, 'settings.html', context)

            request.user.email = email

        request.user.first_name = name
        request.user.save()
    
        prof = UserProfile.objects.raw(f'SELECT * FROM home_userprofile WHERE username = "{request.user.username}"')[0]
        prof.name = name
        prof.bio = bio
        prof.profile_pic = image_base64
        print(image_base64)
        prof.save()

        context = {
            'profile': prof,
            'message': 'Settings updated successfully.',
            'status': 'success'
        }
        return render(request, 'settings.html', context)
    

    
    context = {
        'profile': prof,
    }
    return render(request, 'settings.html', context)