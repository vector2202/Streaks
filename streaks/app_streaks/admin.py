from django.contrib import admin
from .models import Habit, HabitCompletion, Notificacion, PreferenciasNotificacion
@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display =('usuario','mensaje','fecha_creacion')
    list_filter = ('usuario', 'fecha_creacion') 
    search_fields = ('usuario__username', 'mensaje')

@admin.register(PreferenciasNotificacion)
class PreferenciasNotificacionAdmin(admin.ModelAdmin):
    list_display =('usuario','recibir_notificaciones','frecuencia')
    list_filter = ('frecuencia',) 
    search_fields = ('usuario__username',)