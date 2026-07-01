from django.contrib import admin

from .models import Calificacion


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('viaje', 'autor', 'receptor', 'puntuacion', 'creado')
    list_filter = ('puntuacion',)
