from django.contrib import admin

from .models import TicketSoporte, MensajeSoporte


class MensajeSoporteInline(admin.TabularInline):
    model = MensajeSoporte
    extra = 0


@admin.register(TicketSoporte)
class TicketSoporteAdmin(admin.ModelAdmin):
    list_display = ('id', 'asunto', 'usuario', 'categoria', 'estado', 'actualizado')
    list_filter = ('categoria', 'estado')
    inlines = [MensajeSoporteInline]
