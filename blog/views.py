from itertools import count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import Post
from .forms import PostForm
from django.contrib.auth.models import User
from django.db.models import Count

def post_list(request):
    posts = Post.objects.annotate(like_count=Count('likes')).order_by('-like_count')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Check if the user's IP address or session has already liked the post
    user_identifier = request.META.get('REMOTE_ADDR')  # Get user's IP address
    if request.session.get('liked_posts', {}).get(pk):
        # User's IP address or session has already liked the post, so remove the like
        del request.session['liked_posts'][pk]
        post.likes.remove(request.user)
    else:
        # User's IP address or session has not liked the post, so add the like
        request.session.setdefault('liked_posts', {})[pk] = True
        post.likes.add(request.user)

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



