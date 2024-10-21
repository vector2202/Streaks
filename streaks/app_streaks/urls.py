from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.user_register, name='user_register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('create/', views.create_habit, name='create_habit'),
    path('view/', views.view_habits, name='view_habits'),
    #path('progress/', views.progress_view, name='progress'),
]
