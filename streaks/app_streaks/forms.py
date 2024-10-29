from django import forms
from .models import Category, Habit
from django.contrib.auth.models import User

class HabitForm (forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'frequency', 'category', 'goal']
        labels = {
            'name': 'Nombre del Hábito',
            'frequency': 'Frecuencia',
            'category': 'Categoría',
            'goal': 'Meta',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingresa el nombre del hábito'}),
            'frequency': forms.Select(),
            'category': forms.Select(),
            'goal': forms.NumberInput(attrs={'min': 1}),
        }
