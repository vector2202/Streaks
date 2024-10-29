from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    nombre=models.CharField(max_length=50, unique=True)
    def __str__(self):
        return f'{self.nombre}'
    
class Habit(models.Model):
        user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
        name = models.CharField(max_length=100)
        frequency = models.CharField(max_length=50, choices=[
            ('daily', 'Diario'),
            ('weekly', 'Semanal'),
            ('monthly', 'Mensual'),
        ])
        category = models.CharField(max_length=50, choices=[
            ('salud', 'Salud'),
            ('deporte', 'Deporte'),
            ('trabajo', 'Trabajo'),
            ('personal', 'Personal'),
        ],default='uncategorized')
        goal = models.IntegerField(default=1)
        creation_date = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f'{self.name}'
        
        
class HabitCompletion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='completions')
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return f'{self.habit.name} completado el {self.date}' 

class Notificacion(models.Model):
     usuario = models.ForeignKey(User, on_delete= models.CASCADE)
     mensaje = models.TextField()
     leido = models.BooleanField(default=False)
     fecha_creacion = models.DateTimeField(auto_now_add=True)

def __str__(self):
     return f"Notifcación para {self.usuario.username}: {self.mensaje}"     

class PreferenciasNotificacion(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    recibir_notificaciones = models.BooleanField(default=True)
    frecuencia = models.CharField(
        max_length = 10,
        choices = [('diaria','Diaria'), ('semanal','Semanal'), ('mensual', 'Mensual')],
        default = 'semanal'
    )

    def __str__(self):
        return f"Preferencias de {self.usuario.username}"
    
