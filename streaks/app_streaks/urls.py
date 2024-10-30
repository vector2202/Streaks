from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.user_register, name='user_register'),
    path('login/', auth_views.LoginView.as_view(template_name='login/InicioSesion.html'), name='login'),
    path('create/', views.create_habit, name='create_habit'),
    path('view/', views.view_habits, name='view_habits'),
    path('complete_habit/<int:habit_id>/', views.complete_habit, name='complete_habit'),
    path('logout/', views.user_logout, name='logout'),
    #path('progress/', views.progress_view, name='progress'),
    path('configurar_notificaciones/',views.configurar_notifiaciones,name='configurar_notificaciones'),
    path('marcar_notificaciones_leidas/', views.marcar_notificaciones_leidas, name='marcar_notificaciones_leidas'),
    path('decrement_goal/<int:habit_id>/', views.decrement_goal, name='decrement_goal'),
    path('get_habits_stats/', views.get_habits_stats, name='get_habits_stats'),
]

