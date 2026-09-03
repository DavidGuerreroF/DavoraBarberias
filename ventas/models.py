from django.db import models
from django.contrib.auth.models import User


class Venta(models.Model):
    METODO_EFECTIVO = 'efectivo'
    METODO_TRANSFERENCIA = 'transferencia'
    METODO_TARJETA = 'tarjeta'

    METODOS_PAGO = [
        (METODO_EFECTIVO, 'Efectivo'),
        (METODO_TRANSFERENCIA, 'Transferencia'),
        (METODO_TARJETA, 'Tarjeta'),
    ]

    cita = models.OneToOneField(
        'citas.Cita', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='venta'
    )
    barbero = models.ForeignKey(
        'barberos.Barbero', on_delete=models.SET_NULL,
        null=True, related_name='ventas'
    )
    cliente_nombre = models.CharField(max_length=100, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default=METODO_EFECTIVO)
    notas = models.TextField(blank=True)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']

    def __str__(self):
        return f"Venta #{self.pk} - ${self.total} - {self.fecha.strftime('%d/%m/%Y')}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    servicio = models.ForeignKey(
        'servicios.Servicio', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    descripcion = models.CharField(max_length=200)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.descripcion} x{self.cantidad}"

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
