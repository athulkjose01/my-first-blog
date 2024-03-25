from itertools import count
import re
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from .models import Post
from .forms import PostForm
from django.contrib.auth.models import User
from django.db.models import Count
from django.contrib.auth import authenticate, login

def post_list(request):
    posts = Post.objects.annotate(like_count=Count('likes')).order_by('-like_count')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Get the admin user from the User model (replace 'admin_username' with the actual username of your admin user)
    admin_user = User.objects.get(username='admin')

    # Check if the admin user has already liked the post
    if admin_user in post.likes.all():
        post.likes.remove(admin_user)  # If already liked, remove the like (toggle like)
    else:
        post.likes.add(admin_user)  # If not liked, add the like

    return redirect('post_detail', pk=pk)

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = get_default_author()  # Assign default author
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_new.html', {'form': form, 'title': 'Add/Edit Post'})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


def get_default_author():
    default_author, _ = User.objects.get_or_create(username='Anonymous')
    return default_author





