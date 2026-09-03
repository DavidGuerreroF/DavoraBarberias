from django.db import models


class ConfiguracionBarberia(models.Model):
    nombre = models.CharField(max_length=200, default='Mi Barbería')
    slogan = models.CharField(max_length=300, blank=True)
    descripcion = models.TextField(blank=True)
    whatsapp = models.CharField(max_length=20, blank=True, help_text='Número con código de país ej: 573001234567')
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.TextField(blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    facebook = models.CharField(max_length=100, blank=True)
    logo = models.ImageField(upload_to='config/', blank=True, null=True)
    imagen_hero = models.ImageField(upload_to='config/', blank=True, null=True)
    horario_texto = models.TextField(blank=True, help_text='Descripción del horario de atención')
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Configuración'
        verbose_name_plural = 'Configuración de la Barbería'

    def __str__(self):
        return self.nombre

    @classmethod
    def get_config(cls):
        config = cls.objects.filter(activo=True).first()
        if not config:
            config = cls.objects.create(nombre='BarberShop', whatsapp='573001234567')
        return config
