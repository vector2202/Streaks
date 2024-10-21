from django import forms
from .models import Category, Habit

class HabitForm (forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.alll(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='Seleccione una categoria'
    )
    class Meta:
        model = Habit
        fields =['nombre', 'frequencia', 'categoria', 'objetivc']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'frecuencia': forms.Select(attrs={'class': 'form-control'}),
            'objetivo': forms.NumberInput(attrs={'class': 'form-control', 'min': 1})
        }
