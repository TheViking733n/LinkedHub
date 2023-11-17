from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from home.models import UserProfile, Connection, PendingRequest
from post.models import Post
from django.db import connection as db_connection

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
    connections = Connection.objects.raw(f'SELECT * FROM home_connection WHERE user1 = "{username}"')
    connections = len(connections)
    context = {
        'profile': prof,
        'posts': posts,
        'connections': connections,
    }
    if request.user.is_authenticated and request.user.username != username:
        # mutual_connections = UserProfile.objects.raw(f'SELECT * FROM home_userprofile WHERE username = "{request.user.username}"')[0].connections.split(',')
        mutual_connections = ['Not yet implemented.']
        context['mutual_connections'] = mutual_connections
        conn_status = 'not connected'
        if PendingRequest.objects.raw(f'SELECT * FROM home_pendingrequest WHERE sender = "{request.user.username}" AND receiver = "{username}"'):
            conn_status = 'pending'
        elif PendingRequest.objects.raw(f'SELECT * FROM home_pendingrequest WHERE sender = "{username}" AND receiver = "{request.user.username}"'):
            conn_status = 'requested'
        elif Connection.objects.raw(f'SELECT * FROM home_connection WHERE user1 = "{request.user.username}" AND user2 = "{username}"'):
            conn_status = 'connected'
        context['conn_status'] = conn_status

    if request.user.is_authenticated and request.user.username == username:
        ...
        # pending_requests = PendingRequest.objects.raw(f'SELECT * FROM home_pendingrequest WHERE receiver = "{username}"')

        with db_connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT sender, name
                FROM home_pendingrequest
                LEFT JOIN home_userprofile
                ON sender = username
                WHERE receiver = "{request.user.username}";
            ''')

            pending_requests = []
            for row in cursor.fetchall():
                pending_request = {
                    'sender': row[0],
                    'name': row[1],
                }
                pending_requests.append(pending_request)
        context['pending_requests'] = pending_requests
    
    return render(request, 'profile.html', context)



@login_required
def connect_request(request):
    if request.method == 'POST':
        sender = request.user.username
        receiver = request.POST['receiver']
        if sender == receiver:
            return HttpResponse('Error: Cannot send request to yourself.')
        if Connection.objects.raw(f'SELECT * FROM home_connection WHERE user1 = "{sender}" AND user2 = "{receiver}"'):
            return HttpResponse('Error: Already connected.')
        if PendingRequest.objects.raw(f'SELECT * FROM home_pendingrequest WHERE sender = "{sender}" AND receiver = "{receiver}"'):
            return HttpResponse('Error: Request already sent.')
        if PendingRequest.objects.raw(f'SELECT * FROM home_pendingrequest WHERE sender = "{receiver}" AND receiver = "{sender}"'):
            return HttpResponse('Error: Request already received.')
        if receiver not in User.objects.all().values_list('username', flat=True):
            return HttpResponse('Error: Invalid username.')
        pending_request = PendingRequest.objects.create(sender=sender, receiver=receiver)
        pending_request.save()
        return redirect('profile', username=receiver)
    return HttpResponse('403 Forbidden')
        

@login_required
def connect_accept(request):
    if request.method == 'POST':
        sender = request.POST['sender']
        receiver = request.user.username
        if sender == receiver:
            return HttpResponse('Error: Cannot accept request from yourself.')
        if not PendingRequest.objects.raw(f'SELECT * FROM home_pendingrequest WHERE sender = "{sender}" AND receiver = "{receiver}"'):
            return HttpResponse('Error: Request not found.')
        connection = Connection.objects.create(user1=sender, user2=receiver)
        connection = Connection.objects.create(user1=receiver, user2=sender)
        connection.save()
        with db_connection.cursor() as cursor:
            cursor.execute(f'DELETE FROM home_pendingrequest WHERE sender = "{sender}" AND receiver = "{receiver}"')
        
        return redirect('profile', username=sender)
    return HttpResponse('403 Forbidden')



@login_required
def cancel_request(request):
    if request.method == 'POST':
        sender = request.user.username
        receiver = request.POST['receiver']
        if sender == receiver:
            return HttpResponse('Error: Cannot cancel request to yourself.')
        if not PendingRequest.objects.raw(f'SELECT * FROM home_pendingrequest WHERE sender = "{sender}" AND receiver = "{receiver}"'):
            return HttpResponse('Error: Request not found.')
        with db_connection.cursor() as cursor:
            cursor.execute(f'DELETE FROM home_pendingrequest WHERE sender = "{sender}" AND receiver = "{receiver}"')
        return redirect('profile', username=receiver)
    return HttpResponse('403 Forbidden')


@login_required
def connect_reject(request):
    if request.method == 'POST':
        sender = request.POST['sender']
        receiver = request.user.username
        if sender == receiver:
            return HttpResponse('Error: Cannot reject request from yourself.')
        if not PendingRequest.objects.raw(f'SELECT * FROM home_pendingrequest WHERE sender = "{sender}" AND receiver = "{receiver}"'):
            return HttpResponse('Error: Request not found.')
        with db_connection.cursor() as cursor:
            cursor.execute(f'DELETE FROM home_pendingrequest WHERE sender = "{sender}" AND receiver = "{receiver}"')
        return redirect('profile', username=sender)



@login_required
def connect_remove(request):
    if request.method == 'POST':
        user1 = request.user.username
        user2 = request.POST['receiver']
        if user1 == user2:
            return HttpResponse('Error: Cannot remove yourself.')
        if not Connection.objects.raw(f'SELECT * FROM home_connection WHERE user1 = "{user1}" AND user2 = "{user2}"'):
            return HttpResponse('Error: Connection not found.')
        with db_connection.cursor() as cursor:
            cursor.execute(f'DELETE FROM home_connection WHERE user1 = "{user1}" AND user2 = "{user2}"')
            cursor.execute(f'DELETE FROM home_connection WHERE user1 = "{user2}" AND user2 = "{user1}"')
        return redirect('profile', username=user2)




@login_required
def settings(request):
    prof = UserProfile.objects.raw(f'SELECT * FROM home_userprofile WHERE username = "{request.user.username}"')[0]
    
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        bio = request.POST['bio']
        organization = request.POST['organization']
        image_base64 = request.POST['image_base64']

        if organization == request.user.username:
            context = {
                'profile': prof,
                'message': 'Error: Organization cannot be your own username.',
                'status': 'warning'
            }
            return render(request, 'settings.html', context)
        elif organization == '' or UserProfile.objects.raw(f'SELECT * FROM home_userprofile WHERE username = "{organization}"'):
            prof.organization = organization
            prof.save()
        else:
            context = {
                'profile': prof,
                'message': 'Error: Organization does not exist.',
                'status': 'warning'
            }
            return render(request, 'settings.html', context)


        if request.user.email != email:
            if email in User.objects.all().values_list('email', flat=True):
                context = {
                    'profile': prof,
                    'message': 'Error: Email already exists.',
                    'status': 'warning'
                }
                return render(request, 'settings.html', context)

            request.user.email = email
            request.user.save()

        request.user.first_name = name
        request.user.save()
    
        prof = UserProfile.objects.raw(f'SELECT * FROM home_userprofile WHERE username = "{request.user.username}"')[0]
        prof.name = name
        prof.bio = bio
        prof.profile_pic = image_base64
        # print(image_base64)
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