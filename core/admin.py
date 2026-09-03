from django.contrib import admin
from .models import ConfiguracionBarberia


@admin.register(ConfiguracionBarberia)
class ConfiguracionBarberiaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'whatsapp', 'email', 'activo']
    fieldsets = (
        ('Información General', {'fields': ('nombre', 'slogan', 'descripcion', 'logo', 'imagen_hero')}),
        ('Contacto', {'fields': ('whatsapp', 'telefono', 'email', 'direccion')}),
        ('Redes Sociales', {'fields': ('instagram', 'facebook')}),
        ('Horario', {'fields': ('horario_texto',)}),
        ('Estado', {'fields': ('activo',)}),
    )
