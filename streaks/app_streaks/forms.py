from django import forms
from .models import Category, Habit

class HabitForm (forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='Seleccione una categoria'
    )
    class Meta:
        model = Habit
        fields =['name', 'frequency', 'category', 'goal']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'goal': forms.NumberInput(attrs={'class': 'form-control', 'min': 1})
        }
