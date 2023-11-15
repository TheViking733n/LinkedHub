from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from home.models import UserProfile
from post.models import Post, Comment

# Create your views here.

@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        author_id = request.user.username
        post = Post.objects.create(title=title, content=content, author_id=author_id)
        post.save()
        return redirect('view_post', post_id=post.post_id)
    
    return render(request, 'create_post.html')


@login_required
def like_post(request):
    ...


@login_required
def comment_post(request):
    ...


@login_required
def view_post(request, post_id):
    post = Post.objects.get(post_id=post_id)
    author = UserProfile.objects.get(username=post.author_id)
    # comments = []
    # for comment_id in post.comment_ids.split(','):
    #     if comment_id != '':
    #         comment = Comment.objects.get(comment_id=comment_id)
    #         comments.append(comment)
    
    return render(request, 'view_post.html', {'post': post, 'author': author})


