from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import HabitForm
from .models import Habit, HabitCompletion
from django.db.models import Count
from datetime import datetime, timedelta

@login_required
def home(request):
    today = datetime.today().date()
    
    habits = Habit.objects.filter(usuario=request.user)

    completed_today = HabitCompletion.objects.filter(
        habit__in = habits,
        date = today
    ).values_list('habit-id', flat=True)

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
        'completados hoy': habits_completed_today
    }
    return render(request, 'habits/home.html', context)
@login_required
def create_habit(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.usuario = request.user
            habit.save()
            return redirect('view_habits')
    else:
        form = HabitForm()
    return render(request, 'habits/create_habit.html', {'form': form})

@login_required
from django.core.paginator import Paginator

@login_required
def view_habits(request):
    habits = Habit.objects.filter(usuario=request.user)
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
    return render(request, 'habits/view_habits.html', context)


@login_required
def complete_habit(request, habit_id):
    habit = Habit.objects.get(id=habit_id, usuario=request.user)
    today = datetime.today().date()
    completed = HabitCompletion.objects.filter(habit=habit, fecha=today).first()
    if not completed:
        HabitCompletion.objects.create(habit=habit)
        messages.success(request, f"Hábito '{habit.nombre}' completado exitosamente.")
    else:
        messages.info(request, f"Ya has completado el hábito '{habit.nombre}' hoy.")
    
    return redirect('home')

