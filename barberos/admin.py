from django.contrib import admin
from .models import Barbero, HorarioBarbero


class HorarioInline(admin.TabularInline):
    model = HorarioBarbero
    extra = 1


@admin.register(Barbero)
class BarberoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'telefono', 'activo', 'orden']
    list_editable = ['activo', 'orden']
    search_fields = ['nombre', 'apellido']
    inlines = [HorarioInline]


@admin.register(HorarioBarbero)
class HorarioBarberoAdmin(admin.ModelAdmin):
    list_display = ['barbero', 'dia_semana', 'hora_inicio', 'hora_fin', 'activo']
    list_filter = ['barbero', 'activo']
