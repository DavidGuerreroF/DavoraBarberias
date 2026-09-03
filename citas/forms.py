from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Cita
from barberos.models import Barbero
from servicios.models import Servicio
from clientes.models import Cliente


class ReservaPublicaForm(forms.Form):
    """Formulario público de reserva sin necesidad de cuenta."""
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-dark',
            'placeholder': 'Tu nombre completo',
            'autocomplete': 'name',
        }),
        label='Tu nombre'
    )
    whatsapp = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-dark',
            'placeholder': 'Ej: 3001234567',
            'autocomplete': 'tel',
        }),
        label='WhatsApp'
    )
    servicio = forms.ModelChoiceField(
        queryset=Servicio.objects.filter(activo=True),
        widget=forms.Select(attrs={'class': 'form-select form-control-dark', 'id': 'id_servicio'}),
        label='Servicio',
        empty_label='-- Selecciona un servicio --'
    )
    barbero = forms.ModelChoiceField(
        queryset=Barbero.objects.filter(activo=True),
        widget=forms.Select(attrs={'class': 'form-select form-control-dark', 'id': 'id_barbero'}),
        label='Barbero',
        empty_label='-- Selecciona un barbero --',
        required=False
    )
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control form-control-dark',
            'type': 'date',
            'id': 'id_fecha',
        }),
        label='Fecha'
    )
    hora = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control form-control-dark',
            'type': 'time',
            'id': 'id_hora',
        }),
        label='Hora'
    )
    notas = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control form-control-dark',
            'placeholder': 'Alguna indicación especial (opcional)',
            'rows': 3,
        }),
        label='Notas (opcional)'
    )

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha and fecha < timezone.now().date():
            raise ValidationError('No puedes reservar en una fecha pasada.')
        return fecha

    def clean_whatsapp(self):
        whatsapp = self.cleaned_data.get('whatsapp', '').strip()
        limpio = ''.join(c for c in whatsapp if c.isdigit() or c == '+')
        if len(limpio.replace('+', '')) < 7:
            raise ValidationError('Ingresa un número de WhatsApp válido.')
        return limpio

    def verificar_disponibilidad(self):
        """Verifica que no haya otra cita confirmada/pendiente en el mismo horario."""
        barbero = self.cleaned_data.get('barbero')
        fecha = self.cleaned_data.get('fecha')
        hora = self.cleaned_data.get('hora')
        if barbero and fecha and hora:
            existe = Cita.objects.filter(
                barbero=barbero,
                fecha=fecha,
                hora=hora,
                estado__in=[Cita.ESTADO_PENDIENTE, Cita.ESTADO_CONFIRMADA]
            ).exists()
            if existe:
                raise ValidationError(
                    f'Ya existe una cita para {barbero.nombre_completo} a esa hora. '
                    'Por favor elige otro horario.'
                )


class CitaAdminForm(forms.ModelForm):
    """Formulario para gestión de citas en el panel admin."""

    class Meta:
        model = Cita
        fields = [
            'nombre_cliente', 'whatsapp_cliente', 'barbero', 'servicio',
            'fecha', 'hora', 'estado', 'notas', 'notas_admin',
        ]
        widgets = {
            'nombre_cliente': forms.TextInput(attrs={'class': 'form-control form-control-dark'}),
            'whatsapp_cliente': forms.TextInput(attrs={'class': 'form-control form-control-dark'}),
            'barbero': forms.Select(attrs={'class': 'form-select form-control-dark'}),
            'servicio': forms.Select(attrs={'class': 'form-select form-control-dark'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control form-control-dark', 'type': 'date'}),
            'hora': forms.TimeInput(attrs={'class': 'form-control form-control-dark', 'type': 'time'}),
            'estado': forms.Select(attrs={'class': 'form-select form-control-dark'}),
            'notas': forms.Textarea(attrs={'class': 'form-control form-control-dark', 'rows': 3}),
            'notas_admin': forms.Textarea(attrs={'class': 'form-control form-control-dark', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        barbero = cleaned_data.get('barbero')
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')
        estado = cleaned_data.get('estado')

        if barbero and fecha and hora and estado in [Cita.ESTADO_PENDIENTE, Cita.ESTADO_CONFIRMADA]:
            qs = Cita.objects.filter(
                barbero=barbero,
                fecha=fecha,
                hora=hora,
                estado__in=[Cita.ESTADO_PENDIENTE, Cita.ESTADO_CONFIRMADA]
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(
                    f'Ya existe una cita para {barbero.nombre_completo} en esa fecha y hora.'
                )
        return cleaned_data


class BarberoForm(forms.ModelForm):

    class Meta:
        model = Barbero
        fields = ['nombre', 'apellido', 'telefono', 'foto', 'especialidades', 'activo', 'orden']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-dark'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control form-control-dark'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control form-control-dark'}),
            'especialidades': forms.TextInput(attrs={
                'class': 'form-control form-control-dark',
                'placeholder': 'Corte, Barba, Diseño...',
            }),
            'orden': forms.NumberInput(attrs={'class': 'form-control form-control-dark'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ServicioForm(forms.ModelForm):

    class Meta:
        model = Servicio
        fields = ['nombre', 'descripcion', 'precio', 'duracion_minutos', 'imagen', 'activo', 'orden']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-dark'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control form-control-dark', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control form-control-dark', 'step': '0.01'}),
            'duracion_minutos': forms.NumberInput(attrs={'class': 'form-control form-control-dark'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control form-control-dark'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ClienteForm(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'whatsapp', 'email', 'notas']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-dark'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control form-control-dark'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control form-control-dark'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-dark'}),
            'notas': forms.Textarea(attrs={'class': 'form-control form-control-dark', 'rows': 3}),
        }
