from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'whatsapp', 'email', 'creado']
    search_fields = ['nombre', 'apellido', 'whatsapp', 'email']
    readonly_fields = ['creado', 'actualizado']
