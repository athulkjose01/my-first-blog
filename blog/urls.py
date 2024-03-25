from django.urls import path
from . import views
from.views import LoginView, register

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/like/', views.like_post, name='like_post'),
    path('post/new/', views.post_new, name='post_new'),  # URL for creating new post
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/',register, name = "register"),  # URL for editing existing post
]