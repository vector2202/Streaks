from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login
from .forms import HabitForm
from .models import Habit, HabitCompletion, Notificacion, PreferenciasNotificacion
from django.db.models import Count
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.views import View
import json
from datetime import datetime

def user_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Iniciar sesión
            return redirect('home')  # Redirigir a la página de inicio 
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})



@login_required
def home(request):
    today = datetime.today().date()
    
    habits = Habit.objects.filter(user=request.user)

    completed_today = HabitCompletion.objects.filter(
        habit__in = habits,
        date = today
    ).values_list('habit_id', flat=True)

    pendings = []

    for habit in habits:
        if habit.frecuencia == 'diaria':
            completado = HabitCompletion.objects.filter(habit=habit, fecha=today).exists()
            if not completado:
                pendings.append(habit)
        elif habit.frecuencia == 'semanal':
            start_of_week = today - timedelta(days=today.weekday())
            completado = HabitCompletion.objects.filter(habit=habit, fecha__gte=start_of_week, fecha__lte=today).exists()
            if not completado:
                pendings.append(habit)
        elif habit.frecuencia == 'mensual':
            start_of_month = today.replace(day=1)
            completado = HabitCompletion.objects.filter(habit=habit, fecha__gte=start_of_month, fecha__lte=today).exists()
            if not completado:
                pendings.append(habit)
    habits_completed_today = habits.filter(id__in=completed_today)
    context = {
        'pendientes': pendings,
        'completados_hoy': habits_completed_today
    }
    return render(request, 'resumen/Resumen.html', context)

@login_required
def create_habit(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            return redirect('view_habits')
    else:
        form = HabitForm()
    return render(request, 'create/CreacionHabitos.html', {'form': form})

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


@login_required
def complete_habit(request, habit_id):
    habit = Habit.objects.get(id=habit_id, user=request.user)
    today = datetime.today().date()
    completed = HabitCompletion.objects.filter(habit=habit, fecha=today).first()
    if not completed:
        HabitCompletion.objects.create(habit=habit)
        messages.success(request, f"Hábito '{habit.nombre}' completado exitosamente.")
    else:
        messages.info(request, f"Ya has completado el hábito '{habit.nombre}' hoy.")
    
    return redirect('home')

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
           

