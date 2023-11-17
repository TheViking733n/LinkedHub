from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from home.models import UserProfile
from post.models import Post, Comment, Like
from django.db import connection

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
    res = {
        'likes': comment.likes,
    }
    return JsonResponse(res)


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
def delete_item(request):
    if request.method == 'POST':
        item_type = request.POST['item_type']
        item_id = request.POST['item_id']
        if item_type == 'post':
            post = Post.objects.get(post_id=item_id)
            if not post or post.author_id != request.user.username:
                return HttpResponse('You are not authorized to delete this post.')
            post.delete()
            return redirect('profile', username=request.user.username)
        
        elif item_type == 'comment':
            comment = Comment.objects.get(comment_id=item_id)
            if not comment or comment.author_id != request.user.username:
                return HttpResponse('You are not authorized to delete this comment.')
            comment.delete()
            return redirect('view_post', post_id=comment.post_id)

        return HttpResponse('Invalid item type.')
    
    return HttpResponse('403 Forbidden')


@login_required
def view_post(request, post_id):
    post = Post.objects.get(post_id=post_id)
    author = UserProfile.objects.get(username=post.author_id)
    post.views += 1
    post.save()
    # comments = []
    # for comment_id in post.comment_ids.split(','):
    #     if comment_id != '':
    #         comment = Comment.objects.get(comment_id=comment_id)
    #         comments.append(comment)
    # comments = Comment.objects.raw(f'SELECT * FROM post_comment WHERE post_id={post_id} ORDER BY likes DESC')
    # commenters = []
    # for comment in comments:
    #     commenters.append(UserProfile.objects.get(username=comment.author_id))
    
    cursor = connection.cursor()
    cursor.execute(f'''
        SELECT comment_id, post_id, content, author_id, likes, timestamp, name FROM post_comment
        LEFT JOIN home_userprofile
        ON post_comment.author_id = home_userprofile.username
        WHERE post_id={post_id}
        ORDER BY likes DESC;
    ''')

    comments = []
    for row in cursor.fetchall():
        comment = {
            'comment_id': row[0],
            'post_id': row[1],
            'content': row[2],
            'author_id': row[3],
            'likes': row[4],
            'timestamp': row[5],
            'name': row[6],
        }
        comments.append(comment)
    # print(comments)

    return render(request, 'view_post.html', {'post': post, 'author': author, 'comments': comments})


