from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login, logout
from .forms import HabitForm
from .models import Habit, HabitCompletion, Notificacion, PreferenciasNotificacion
from django.db.models import Count
from datetime import datetime, timedelta, timezone
from django.core.paginator import Paginator
from django.views import View
import json
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

def user_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            print("Registro exitoso")
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register/Registro.html', {'form': form})



@login_required
def home(request):
    today = datetime.today().date()
    habits = Habit.objects.filter(user=request.user, creation_date__date__lte=today)
    completed_today = HabitCompletion.objects.filter(
        habit__in = habits,
        date = today
    ).values_list('habit_id', flat=True)
    print(completed_today)
    print(habits)
    pendings = []
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    for habit in habits:
        if habit.frequency == 'daily':
            completado = HabitCompletion.objects.filter(habit_id=habit.id, date=today).exists()
            print(completado)
            if not completado:
                pendings.append(habit)
        elif habit.frequency == 'weekly':
            completado = HabitCompletion.objects.filter(habit_id=habit.id, date__gte=start_of_week, date__lte=today).exists()
            if not completado:
                pendings.append(habit)
        elif habit.frequency == 'monthly':
            
            completado = HabitCompletion.objects.filter(habit_id=habit.id, date__gte=start_of_month, date__lte=today).exists()
            if not completado:
                pendings.append(habit)
    print(pendings)
    habits_completed_today = habits.filter(id__in=completed_today)
    user_name = request.user
    print(Habit.objects.filter(user=user_name, creation_date__date=today))
    sts_daily = calcular_porcentaje_habitos(Habit.objects.filter(user=user_name, creation_date__date=today))
    sts_weekly = calcular_porcentaje_habitos(Habit.objects.filter(user=user_name, creation_date__date__gte=start_of_week, creation_date__date__lte=today))
    sts_monthly = calcular_porcentaje_habitos(Habit.objects.filter(user=user_name, creation_date__date__gte=start_of_month, creation_date__date__lte=today))
    print(sts_daily, sts_weekly, sts_monthly)
    context = {
        'pendientes': pendings,
        'completados_hoy': habits_completed_today,
        'user_name': user_name,
        'estadistica_diaria': sts_daily,
        'estadistica_semanal': sts_weekly,
        'estadistica_mensual': sts_monthly
    }
    return render(request, 'resumen/Resumen.html', context)

@login_required
def create_habit(request):
    if request.method == 'POST':
        name = request.POST.get("name")
        frequency = request.POST.get("frequency")
        category = request.POST.get("category")
        goal = request.POST.get("goal")
        form = HabitForm(request.POST)
        print(form)
        if form.is_valid():
            Habit.objects.create(
                name=name,
                frequency=frequency,
                user=request.user,
                category=category,
                goal=goal,
                original_goal=goal,
                creation_date=timezone.now()
            )
            return redirect('home')
    else:
        form = HabitForm()

    return render(request, 'create/CreacionHabitos.html', {'form': form})

def calculate_next_date(start_date, day):
    days_of_week = {
        'lunes': 0,
        'martes': 1,
        'miércoles': 2,
        'jueves': 3,
        'viernes': 4,
        'sábado': 5,
        'domingo': 6,
    }
    
    today_weekday = start_date.weekday()
    target_weekday = days_of_week[day]
    
    if target_weekday <= today_weekday:
        next_date = start_date + timedelta(days=(7 + target_weekday - today_weekday))
    else:
        next_date = start_date + timedelta(days=(target_weekday - today_weekday))
    
    return next_date
@login_required
def get_habits_stats(request):
    start_date = request.GET.get('fecha_inicio')
    end_date = request.GET.get('fecha_fin')
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    habits = Habit.objects.filter(user=request.user, date__gte=start_date, date__lte=end_date)
    porcentaje = calcular_porcentaje_habitos(habits)
    context = {
        'porcentaje': porcentaje
    }
    return render(request, 'resume/Resumen.html', context)
@login_required
def view_habits(request):
    habits = Habit.objects.filter(user=request.user)
    today = datetime.today().date()
    categoria_id = request.GET.get('categoria')
    if categoria_id and categoria_id.isdigit():
        habits = habits.filter(categoria__id=categoria_id)

    start_date = request.GET.get('fecha_inicio')
    end_date = request.GET.get('fecha_fin')
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            habits = habits.filter(creado_en__date__gte=start_date, creado_en__date__lte=end_date)
        except ValueError:
            pass  

    habit_stats = []
    for habit in habits:
        completions = habit.completions.count()
        if habit.frecuencia == 'diaria':
            days = (today - habit.creado_en.date()).days or 1
            objetivo_total = habit.objetivo * days
        elif habit.frecuencia == 'semanal':
            weeks = ((today - habit.creado_en.date()).days // 7) or 1
            objetivo_total = habit.objetivo * weeks
        elif habit.frecuencia == 'mensual':
            months = ((today.year - habit.creado_en.year) * 12 + today.month - habit.creado_en.month) or 1
            objetivo_total = habit.objetivo * months
        porcentaje = (completions / objetivo_total) * 100 if objetivo_total > 0 else 0
        tiempo_consistencia = completions  # Puedes refinar este cálculo según sea necesario
        habit_stats.append({
            'habit': habit,
            'completions': completions,
            'porcentaje': porcentaje,
            'tiempo_consistencia': tiempo_consistencia,
        })
    #Agregar una lista de completados por dia/semana/mes
    #[4.5.6.7.8]
    # Obtener todas las categorías para el filtro
    categorias = Category.objects.all()

    context = {
        'habit_stats': habit_stats,
        'categorias': categorias,
        'filtro_categoria': categoria_id,
        'filtro_fecha_inicio': start_date,
        'filtro_fecha_fin': end_date,
    }
    return render(request, 'resumen/Resumen.html', context)

def calcular_porcentaje_habitos(habits):
    total_porcentaje = 0
    habit_count = 0

    for habit in habits:
        original_goal = habit.original_goal
        if original_goal > 0:
            actual_goal = habit.goal
            porcentaje_habit = ((original_goal - actual_goal) / original_goal) * 100
            total_porcentaje += porcentaje_habit
            habit_count += 1

    return total_porcentaje / habit_count if habit_count > 0 else 0

def complete_habit(request, habit_id):
    habit = Habit.objects.get(id=habit_id, user=request.user)
    today = datetime.today().date()
    completed = HabitCompletion.objects.filter(habit=habit, date=today).first()
    if not completed:
        HabitCompletion.objects.create(habit=habit,
                                       date=today)
        messages.success(request, f"Hábito '{habit.name}' completado exitosamente.")
        
        if habit.frequency == 'daily':
            next_date = today + timedelta(days=1)
        elif habit.frequency == 'weekly':
            next_date = today + timedelta(weeks=1)
        elif habit.frequency == 'monthly':
            next_date = today.replace(day=1) + timedelta(days=31)
            next_date = next_date.replace(day=1)  # Ajusta al primer día del próximo mes
        else:
            next_date = None
        print("Next date")
        print(next_date)
        # Crea una nueva instancia de Habit para el próximo período
        if next_date:
            Habit.objects.create(
                name=habit.name,
                frequency=habit.frequency,
                category=habit.category,
                goal=habit.original_goal,
                original_goal=habit.original_goal,
                user=request.user,
                creation_date=next_date  
            )
    else:
        messages.info(request, f"Ya has completado el hábito '{habit.name}' hoy.")

def decrement_goal(request, habit_id):
    if request.method == 'POST':
        print("decrement goal")
        try:
            habit = Habit.objects.get(id=habit_id)
            if habit.goal > 0:
                habit.goal -= 1
                habit.save()
            if habit.goal == 0:
                complete_habit(request, habit.id)
            return JsonResponse({'status': 'success', 'goal': habit.goal}, status=200)
        except Habit.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Hábito no encontrado'}, status=404)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

def enviar_notificaciones():
    hoy = datetime.now()

    usuarios_diarios = PreferenciasNotificacion.objects.filter(frecuencia='diaria')
    usuarios_semanales = PreferenciasNotificacion.objects.filter(frecuencia='semanal')
    usuarios_mensuales = PreferenciasNotificacion.objects.filter(frecuencia='mensual')

    for preferencias in usuarios_diarios:
        Notificacion.objects.create(usuario=preferencias.usuario, mensaje="¡Recordatorio diaro!")

    if hoy.weekday() == 0:  # Enviar notificaciones semanales solo los lunes
        for preferencias in usuarios_semanales:
            Notificacion.objects.create(usuario=preferencias.usuario, mensaje="¡Recordatorio semanal!")

    if hoy.day == 1:  # Enviar notificaciones mensuales solo el primer día del mes
        for preferencias in usuarios_mensuales:
            Notificacion.objects.create(usuario=preferencias.usuario, mensaje="¡Recordatorio mensual!")
@login_required
def configurar_notifiaciones(request):
    usuario = request.user
    try:
        preferencias = PreferenciasNotificacion.objects.get(usuario=usuario)
    except PreferenciasNotificacion.DoesNotExist:
        preferencias = PreferenciasNotificacion(usuario=usuario)
    if request.method == 'POST':
        recibir_notificaciones = request.POST.get('recibir_notificaciones',False) == 'on'
        frecuenica = request.POST.get('frecuencia', 'semanal')


        preferencias.recibir_notificaciones = recibir_notificaciones
        preferencias.frecuencia = frecuenica
        preferencias.save()

        return redirect('inicio')

    # Obtener notificaciones del usuario (leídas y no leídas)
    notificaciones = Notificacion.objects.filter(usuario=usuario).order_by('-fecha_creacion')

    contexto = {
        'preferencias': preferencias,
        'notificaciones': notificaciones,  # Pasar todas las notificaciones
    }
    return render(request, 'configurar_notificaciones.html', contexto)

@login_required
def marcar_notificaciones_leidas(request):
    if request.method == 'POST':
        try:

            usuario = request.user

            # Marcar todas las notificaciones del usuario como leídas
            Notificacion.objects.filter(usuario=usuario, leido=False).update(leido=True)
         
            return JsonResponse({'status': 'ok'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=400)
           
def user_logout(request):
    logout(request)
    return redirect('login')
