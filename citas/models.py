from django.db import models
from django.utils import timezone


class Cita(models.Model):
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_CONFIRMADA = 'confirmada'
    ESTADO_ATENDIDA = 'atendida'
    ESTADO_CANCELADA = 'cancelada'
    ESTADO_NO_ASISTIO = 'no_asistio'

    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_CONFIRMADA, 'Confirmada'),
        (ESTADO_ATENDIDA, 'Atendida'),
        (ESTADO_CANCELADA, 'Cancelada'),
        (ESTADO_NO_ASISTIO, 'No asistió'),
    ]

    ESTADO_COLORES = {
        ESTADO_PENDIENTE: 'warning',
        ESTADO_CONFIRMADA: 'info',
        ESTADO_ATENDIDA: 'success',
        ESTADO_CANCELADA: 'danger',
        ESTADO_NO_ASISTIO: 'secondary',
    }

    # Datos del cliente (sin necesidad de cuenta)
    nombre_cliente = models.CharField(max_length=100)
    whatsapp_cliente = models.CharField(max_length=20)

    # Relaciones
    barbero = models.ForeignKey(
        'barberos.Barbero', on_delete=models.SET_NULL,
        null=True, related_name='citas'
    )
    servicio = models.ForeignKey(
        'servicios.Servicio', on_delete=models.SET_NULL,
        null=True, related_name='citas'
    )
    cliente = models.ForeignKey(
        'clientes.Cliente', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='citas'
    )

    # Fecha y hora
    fecha = models.DateField()
    hora = models.TimeField()

    # Estado y notas
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_PENDIENTE)
    notas = models.TextField(blank=True)
    notas_admin = models.TextField(blank=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['fecha', 'hora']

    def __str__(self):
        return f"{self.nombre_cliente} - {self.fecha} {self.hora} - {self.get_estado_display()}"

    @property
    def color_estado(self):
        return self.ESTADO_COLORES.get(self.estado, 'secondary')

    @property
    def es_hoy(self):
        return self.fecha == timezone.now().date()

    def get_whatsapp_url(self):
        numero = self.whatsapp_cliente.replace('+', '').replace(' ', '').replace('-', '')
        if self.servicio and self.barbero:
            mensaje = (
                f"Hola {self.nombre_cliente}! Tu cita ha sido confirmada para el "
                f"{self.fecha.strftime('%d/%m/%Y')} a las {self.hora.strftime('%H:%M')} "
                f"con {self.barbero.nombre_completo} para {self.servicio.nombre}. "
                f"Te esperamos!"
            )
        else:
            mensaje = f"Hola {self.nombre_cliente}! Tu cita ha sido confirmada."
        import urllib.parse
        return f"https://wa.me/{numero}?text={urllib.parse.quote(mensaje)}"

    def get_whatsapp_reserva_url(self, barberia_whatsapp):
        """URL para enviar solicitud de reserva al WhatsApp de la barbería"""
        numero = barberia_whatsapp.replace('+', '').replace(' ', '').replace('-', '')
        mensaje = (
            f"Hola! Quisiera reservar una cita.\n"
            f"Nombre: {self.nombre_cliente}\n"
            f"Servicio: {self.servicio.nombre if self.servicio else 'N/A'}\n"
            f"Barbero: {self.barbero.nombre_completo if self.barbero else 'Cualquiera'}\n"
            f"Fecha: {self.fecha.strftime('%d/%m/%Y')}\n"
            f"Hora: {self.hora.strftime('%H:%M')}\n"
            f"WhatsApp: {self.whatsapp_cliente}"
        )
        import urllib.parse
        return f"https://wa.me/{numero}?text={urllib.parse.quote(mensaje)}"
