from django.db import models


class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    duracion_minutos = models.PositiveIntegerField(default=30)
    imagen = models.ImageField(upload_to='servicios/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"
