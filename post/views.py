from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from home.models import UserProfile
from post.models import Post, Comment, Like

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


def like_post(request):   # like or unlike a post
    post_id = request.GET['item_id']
    user_id = request.user.username
    if Like.objects.filter(item_id=post_id, item_type='post', user_id=user_id).exists():
        like = Like.objects.get(item_id=post_id, item_type='post', user_id=user_id)
        like.delete()
        post = Post.objects.get(post_id=post_id)
        post.likes -= 1
        post.save()
    else:
        like = Like.objects.create(item_id=post_id, item_type='post', user_id=user_id)
        like.save()
        post = Post.objects.get(post_id=post_id)
        post.likes += 1
        post.save()
    post = Post.objects.raw(f'SELECT * FROM post_post WHERE post_id={post_id}')[0]
    res = {
        'likes': post.likes,
    }
    return JsonResponse(res)


def like_comment(request):   # like or unlike a comment
    comment_id = request.GET['item_id']
    user_id = request.user.username
    if Like.objects.filter(item_id=comment_id, item_type='comment', user_id=user_id).exists():
        like = Like.objects.get(item_id=comment_id, item_type='comment', user_id=user_id)
        like.delete()
        comment = Comment.objects.get(comment_id=comment_id)
        comment.likes -= 1
        comment.save()
    else:
        like = Like.objects.create(item_id=comment_id, item_type='comment', user_id=user_id)
        like.save()
        comment = Comment.objects.get(comment_id=comment_id)
        comment.likes += 1
        comment.save()
    comment = Comment.objects.raw(f'SELECT * FROM post_comment WHERE comment_id={comment_id}')[0]
    return HttpResponse(comment.likes)


@login_required
def like_item(request):
    item_type = request.GET['item_type']
    if item_type == 'post':
        return like_post(request)
    elif item_type == 'comment':
        return like_comment(request)
    else:
        return HttpResponse('Invalid item type.')



@login_required
def comment_post(request):    # comment on a post
    post_id = request.POST['post_id']
    content = request.POST['content']
    author_id = request.user.username
    comment = Comment.objects.create(post_id=post_id, content=content, author_id=author_id)
    comment.save()
    post = Post.objects.raw(f'SELECT * FROM post_post WHERE post_id={post_id}')[0]
    post.comments += 1
    post.save()
    return redirect('view_post', post_id=post_id)


@login_required
def view_post(request, post_id):
    post = Post.objects.get(post_id=post_id)
    author = UserProfile.objects.get(username=post.author_id)
    # comments = []
    # for comment_id in post.comment_ids.split(','):
    #     if comment_id != '':
    #         comment = Comment.objects.get(comment_id=comment_id)
    #         comments.append(comment)
    comments = Comment.objects.raw(f'SELECT * FROM post_comment WHERE post_id={post_id} ORDER BY likes DESC')
    
    return render(request, 'view_post.html', {'post': post, 'author': author, 'comments': comments})


