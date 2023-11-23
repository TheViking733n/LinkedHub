from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, Http404
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
        is_organization = request.POST.get('is_organization')
        if is_organization:
            is_organization = True
        else:
            is_organization = False
        messages = []
        if len(username) < 3:
            messages.append('Username must be at least 3 characters long.')
        if username.isalnum() == False:
            messages.append('Username must contain only letters and numbers.')
        if password1 != password2:
            messages.append('Passwords do not match.')
        if username in User.objects.all().values_list('username', flat=True):
            messages.append('Username already exists.')
        if email in User.objects.all().values_list('email', flat=True):
            messages.append('Email already exists.')
        
        if len(messages) > 0:
            return render(request, 'signup.html', {'messages': messages})
        
        user = User.objects.create_user(first_name=name, username=username, email=email, password=password1)
        # user_profile = UserProfile.objects.create(name=name, username=username)
        # user_profile.is_organization = is_organization
        # user_profile.save()
        user.save()
        with db_connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO home_userprofile (username, name, profile_pic, bio, organization, is_organization)
                VALUES ('{username}', '{name}', '', '', '', {is_organization});
            """)
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
    if username == 'favicon.ico':
        return HttpResponse('404 Not Found')
    try:
        prof = UserProfile.objects.raw(f"SELECT * FROM home_userprofile WHERE username = '{username}'")[0]
    except:
        return render(request, '404.html')
    posts = Post.objects.raw(f"SELECT * FROM post_post WHERE author_id = '{username}' ORDER BY timestamp DESC")
    # connections = prof.connections.split(',')
    connections = Connection.objects.raw(f"SELECT * FROM home_connection WHERE user1 = '{username}'")
    connections = len(connections)
    context = {
        'profile': prof,
        'posts': posts,
        'connections': connections,
    }
    if request.user.is_authenticated and request.user.username != username:
        # mutual_connections = UserProfile.objects.raw(f'SELECT * FROM home_userprofile WHERE username = "{request.user.username}"')[0].connections.split(',')
        # mutual_connections = ['Not yet implemented.']
        with db_connection.cursor() as cursor:
            u, v = request.user.username, username
            cursor.execute(f"""SELECT mutualConnections('{u}', '{v}');""")
            mutual_connections = cursor.fetchall()
            print(mutual_connections)
            _mutual_connections = []
            for row in mutual_connections:
                _mutual_connections.append({
                    'username': row[0],
                })
            mutual_connections = _mutual_connections
            cursor.execute(f"""SELECT secondMutualConnectionsFunc('{u}', '{v}');""")
            secondmutual_connections = cursor.fetchall()
            print(secondmutual_connections)
            _secondmutual_connections = []
            for row in secondmutual_connections:
                _secondmutual_connections.append({
                    'username': row[0],
                })
            secondmutual_connections = _secondmutual_connections

        context['mutual_connections'] = mutual_connections
        context['secondmutual_connections'] = secondmutual_connections
        conn_status = 'not connected'
        if PendingRequest.objects.raw(f"SELECT * FROM home_pendingrequest WHERE sender = '{request.user.username}' AND receiver = '{username}'"):
            conn_status = 'pending'
        elif PendingRequest.objects.raw(f"SELECT * FROM home_pendingrequest WHERE sender = '{username}' AND receiver = '{request.user.username}'"):
            conn_status = 'requested'
        elif Connection.objects.raw(f"SELECT * FROM home_connection WHERE user1 = '{request.user.username}' AND user2 = '{username}'"):
            conn_status = 'connected'
        context['conn_status'] = conn_status

    if prof.organization:
        organization = UserProfile.objects.raw(f"SELECT * FROM home_userprofile WHERE username = '{prof.organization}'")[0]
        context['organization'] = organization
    
    if request.user.is_authenticated and request.user.username == username:
        if prof.organization:
            suggestions = UserProfile.objects.raw(f"SELECT * FROM home_userprofile WHERE organization = '{prof.organization}' AND username != '{username}' AND username NOT IN (SELECT user2 FROM home_connection WHERE user1 = '{username}')")
            context['suggestions'] = suggestions

        # pending_requests = PendingRequest.objects.raw(f'SELECT * FROM home_pendingrequest WHERE receiver = "{username}"')
        with db_connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT sender, name
                FROM home_pendingrequest
                LEFT JOIN home_userprofile
                ON sender = username
                WHERE receiver = '{request.user.username}';
            """)

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
        if Connection.objects.raw(f'SELECT * FROM home_connection WHERE user1 = "{sender}" AND user2 = "{receiver}"'.replace('"', "'")):
            return HttpResponse('Error: Already connected.')
        if PendingRequest.objects.raw(f'SELECT * FROM home_pendingrequest WHERE sender = "{sender}" AND receiver = "{receiver}"'.replace('"', "'")):
            return HttpResponse('Error: Request already sent.')
        if PendingRequest.objects.raw(f'SELECT * FROM home_pendingrequest WHERE sender = "{receiver}" AND receiver = "{sender}"'.replace('"', "'")):
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
        if not PendingRequest.objects.raw(f'SELECT * FROM home_pendingrequest WHERE sender = "{sender}" AND receiver = "{receiver}"'.replace('"', "'")):
            return HttpResponse('Error: Request not found.')
        connection = Connection.objects.create(user1=sender, user2=receiver)
        connection = Connection.objects.create(user1=receiver, user2=sender)
        connection.save()
        with db_connection.cursor() as cursor:
            # cursor.execute(f'DELETE FROM home_pendingrequest WHERE sender = "{sender}" AND receiver = "{receiver}"'.replace('"', "'"))
            cursor.execute(f"CALL deleterequests('{receiver}', '{sender}')")
        
        return redirect('profile', username=sender)
    return HttpResponse('403 Forbidden')



@login_required
def cancel_request(request):
    if request.method == 'POST':
        sender = request.user.username
        receiver = request.POST['receiver']
        if sender == receiver:
            return HttpResponse('Error: Cannot cancel request to yourself.')
        if not PendingRequest.objects.raw(f'SELECT * FROM home_pendingrequest WHERE sender = "{sender}" AND receiver = "{receiver}"'.replace('"', "'")):
            return HttpResponse('Error: Request not found.')
        with db_connection.cursor() as cursor:
            # cursor.execute(f'DELETE FROM home_pendingrequest WHERE sender = "{sender}" AND receiver = "{receiver}"'.replace('"', "'"))
            cursor.execute(f"CALL deleterequests('{receiver}', '{sender}')")
        return redirect('profile', username=receiver)
    return HttpResponse('403 Forbidden')


@login_required
def connect_reject(request):
    if request.method == 'POST':
        sender = request.POST['sender']
        receiver = request.user.username
        if sender == receiver:
            return HttpResponse('Error: Cannot reject request from yourself.')
        if not PendingRequest.objects.raw(f'SELECT * FROM home_pendingrequest WHERE sender = "{sender}" AND receiver = "{receiver}"'.replace('"', "'")):
            return HttpResponse('Error: Request not found.')
        with db_connection.cursor() as cursor:
            # cursor.execute(f'DELETE FROM home_pendingrequest WHERE sender = "{sender}" AND receiver = "{receiver}"'.replace('"', "'"))
            cursor.execute(f"CALL deleterequests('{receiver}', '{sender}')")
        return redirect('profile', username=sender)



@login_required
def connect_remove(request):
    if request.method == 'POST':
        user1 = request.user.username
        user2 = request.POST['receiver']
        if user1 == user2:
            return HttpResponse('Error: Cannot remove yourself.')
        if not Connection.objects.raw(f'SELECT * FROM home_connection WHERE user1 = "{user1}" AND user2 = "{user2}"'.replace('"', "'")):
            return HttpResponse('Error: Connection not found.')
        with db_connection.cursor() as cursor:
            cursor.execute(f'DELETE FROM home_connection WHERE user1 = "{user1}" AND user2 = "{user2}"'.replace('"', "'"))
            cursor.execute(f'DELETE FROM home_connection WHERE user1 = "{user2}" AND user2 = "{user1}"'.replace('"', "'"))
        return redirect('profile', username=user2)




@login_required
def settings(request):
    prof = UserProfile.objects.raw(f'SELECT * FROM home_userprofile WHERE username = "{request.user.username}"'.replace('"', "'"))[0]
    organizations = UserProfile.objects.raw(f'SELECT * FROM home_userprofile WHERE is_organization = true AND username != "{request.user.username}"'.replace('"', "'"))
    
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        bio = request.POST['bio']
        organization = request.POST['organization']
        image_base64 = request.POST['image_base64']

        if organization == request.user.username:
            context = {
                'profile': prof,
                'organizations': organizations,
                'message': 'Error: Organization cannot be your own username.',
                'status': 'warning'
            }
            return render(request, 'settings.html', context)
        elif organization == '' or UserProfile.objects.raw(f'SELECT * FROM home_userprofile WHERE username = "{organization}"'.replace('"', "'")):
            # remove connection from previous organization
            if Connection.objects.raw(f'SELECT * FROM home_connection WHERE user1 = "{request.user.username}" AND user2 = "{prof.organization}"'.replace('"', "'")):
                with db_connection.cursor() as cursor:
                    cursor.execute(f'DELETE FROM home_connection WHERE user1 = "{request.user.username}" AND user2 = "{prof.organization}"'.replace('"', "'"))
                    cursor.execute(f'DELETE FROM home_connection WHERE user1 = "{prof.organization}" AND user2 = "{request.user.username}"'.replace('"', "'"))
            # add connection to new organization
            if not Connection.objects.raw(f'SELECT * FROM home_connection WHERE user1 = "{request.user.username}" AND user2 = "{organization}"'.replace('"', "'")):
                connection = Connection.objects.create(user1=request.user.username, user2=organization)
                connection.save()
                connection = Connection.objects.create(user1=organization, user2=request.user.username)
                connection.save()
            prof.organization = organization
            prof.save()
        else:
            context = {
                'profile': prof,
                'organizations': organizations,
                'message': 'Error: Organization does not exist.',
                'status': 'warning'
            }
            return render(request, 'settings.html', context)


        if request.user.email != email:
            if email in User.objects.all().values_list('email', flat=True):
                context = {
                    'profile': prof,
                    'organizations': organizations,
                    'message': 'Error: Email already exists.',
                    'status': 'warning'
                }
                return render(request, 'settings.html', context)

            request.user.email = email
            request.user.save()

        request.user.first_name = name
        request.user.save()
    
        prof = UserProfile.objects.raw(f'SELECT * FROM home_userprofile WHERE username = "{request.user.username}"'.replace('"', "'"))[0]
        prof.name = name
        prof.bio = bio
        prof.profile_pic = image_base64
        # print(image_base64)
        prof.save()
        
        context = {
            'profile': prof,
            'organizations': organizations,
            'message': 'Settings updated successfully.',
            'status': 'success'
        }
        return render(request, 'settings.html', context)
    

    context = {
        'profile': prof,
        'organizations': organizations,
    }
    return render(request, 'settings.html', context)