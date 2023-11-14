from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
# Create your views here.

def home(request):
    return render(request, 'home/index.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
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
            return render(request, 'home/signup.html', {'messages': messages})
        
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        return redirect('login')
    
    return render(request, 'home/signup.html')


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
            return render(request, 'home/login.html', {'message': 'Invalid credentials.'})
    
    return render(request, 'home/login.html')


def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('home')
        