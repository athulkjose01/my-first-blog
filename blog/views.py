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

    # Check if the user has already liked the post
    if request.user.is_authenticated and request.user in post.likes.all():
        post.likes.remove(request.user)
    elif request.user.is_authenticated:
        post.likes.add(request.user)  # Add the user to the likes
    # Handle the case for anonymous users (optional)
    else:
        # Handle how you want to deal with likes for anonymous users (e.g., redirect to login page)
        return redirect('login')  # Redirect to the login page

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


class LoginView(View):
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("user:user_show_list")
        else:
            error_message = "Incorrect username or password!"
            return render(request, self.template_name, {'error_message': error_message})


def register(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Password confirmation check
        if password != confirm_password:
            error_message = "Password don't match."
            return render(request, 'register.html', {'error_message': error_message})

        # Password length check
        if len(password) < 8:
            error_message = "Password must be at least 8 characters long."
            return render(request, 'register.html', {'error_message': error_message})

        # Password complexity check
        if not any(char.isupper() for char in password) or \
           not any(char.islower() for char in password) or \
           not any(char in "!@#$%^&*()-_+=<>,.?/:;{}[]|\\~" for char in password):
            error_message = "Password must contain at least one uppercase letter, one lowercase letter, and one special character."
            return render(request, 'register.html', {'error_message': error_message})

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            error_message = "This username is already taken. Please choose a different one."
            return render(request, 'register.html', {'error_message': error_message})

        if User.objects.filter(email=email).exists():
            error_message = "This email is already taken. Please use a different one."
            return render(request, 'register.html', {'error_message': error_message})
        
        # Email format check using regular expressions
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            error_message = "Invalid email format. Please enter a valid email address."
            return render(request, 'register.html', {'error_message': error_message})
        
        myuser = User.objects.create_user(username=username, email=email, password=password)

        # Set the name for the user
        myuser.first_name = name
        myuser.save()

        return redirect('http://127.0.0.1:8000/login/')

    return render(request, 'register.html')



