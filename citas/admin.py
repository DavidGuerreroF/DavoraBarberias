from django.contrib import admin
from .models import Cita


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ['nombre_cliente', 'whatsapp_cliente', 'barbero', 'servicio', 'fecha', 'hora', 'estado']
    list_filter = ['estado', 'fecha', 'barbero']
    search_fields = ['nombre_cliente', 'whatsapp_cliente']
    list_editable = ['estado']
    date_hierarchy = 'fecha'
    readonly_fields = ['creado', 'actualizado']
    fieldsets = (
        ('Cliente', {'fields': ('nombre_cliente', 'whatsapp_cliente', 'cliente')}),
        ('Cita', {'fields': ('barbero', 'servicio', 'fecha', 'hora', 'estado')}),
        ('Notas', {'fields': ('notas', 'notas_admin')}),
        ('Registro', {'fields': ('creado', 'actualizado')}),
    )
