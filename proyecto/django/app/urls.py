from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_habit, name='create_habit'),
    path('view/', views.view_habits, name='view_habits'),
    path('progress/', views.progress_view, name='progress'),
]
