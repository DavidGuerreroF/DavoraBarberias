from django.db import models


class Barbero(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    foto = models.ImageField(upload_to='barberos/', blank=True, null=True)
    especialidades = models.TextField(blank=True, help_text='Especialidades separadas por coma')
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Barbero'
        verbose_name_plural = 'Barberos'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def get_especialidades_lista(self):
        if self.especialidades:
            return [e.strip() for e in self.especialidades.split(',')]
        return []


class HorarioBarbero(models.Model):
    DIAS = [
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'),
        (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo'),
    ]
    barbero = models.ForeignKey(Barbero, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.IntegerField(choices=DIAS)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'
        unique_together = ['barbero', 'dia_semana']

    def __str__(self):
        return f"{self.barbero} - {self.get_dia_semana_display()}"
