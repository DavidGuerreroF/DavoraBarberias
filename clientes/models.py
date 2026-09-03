from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True)
    whatsapp = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    notas = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} {self.apellido}".strip()

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}".strip()

    def get_whatsapp_url(self):
        numero = self.whatsapp.replace('+', '').replace(' ', '').replace('-', '')
        return f"https://wa.me/{numero}"
