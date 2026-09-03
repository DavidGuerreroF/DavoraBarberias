from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Cita
from .forms import ReservaPublicaForm
from barberos.models import Barbero
from servicios.models import Servicio
from core.models import ConfiguracionBarberia
import urllib.parse


def reservar(request):
    config = ConfiguracionBarberia.get_config()
    servicios = Servicio.objects.filter(activo=True)
    barberos = Barbero.objects.filter(activo=True)

    if request.method == 'POST':
        form = ReservaPublicaForm(request.POST)
        if form.is_valid():
            try:
                form.verificar_disponibilidad()
            except Exception as e:
                messages.error(request, str(e))
                return render(request, 'public/reservar.html', {
                    'form': form, 'config': config,
                    'servicios': servicios, 'barberos': barberos, 'page': 'reservar',
                })

            cita = Cita(
                nombre_cliente=form.cleaned_data['nombre'],
                whatsapp_cliente=form.cleaned_data['whatsapp'],
                servicio=form.cleaned_data['servicio'],
                barbero=form.cleaned_data.get('barbero'),
                fecha=form.cleaned_data['fecha'],
                hora=form.cleaned_data['hora'],
                notas=form.cleaned_data.get('notas', ''),
                estado=Cita.ESTADO_PENDIENTE,
            )
            cita.save()

            # Generar URL de WhatsApp para enviar solicitud
            whatsapp_url = cita.get_whatsapp_reserva_url(config.whatsapp)

            return render(request, 'public/reserva_exitosa.html', {
                'cita': cita,
                'config': config,
                'whatsapp_url': whatsapp_url,
                'page': 'reservar',
            })
    else:
        # Pre-llenar servicio si viene por parámetro
        initial = {}
        servicio_id = request.GET.get('servicio')
        barbero_id = request.GET.get('barbero')
        if servicio_id:
            initial['servicio'] = servicio_id
        if barbero_id:
            initial['barbero'] = barbero_id
        form = ReservaPublicaForm(initial=initial)

    return render(request, 'public/reservar.html', {
        'form': form,
        'config': config,
        'servicios': servicios,
        'barberos': barberos,
        'page': 'reservar',
    })


def horas_disponibles(request):
    """API para obtener horas disponibles de un barbero en una fecha."""
    barbero_id = request.GET.get('barbero_id')
    fecha_str = request.GET.get('fecha')

    if not barbero_id or not fecha_str:
        return JsonResponse({'horas': []})

    try:
        from datetime import date, time
        fecha = date.fromisoformat(fecha_str)
        barbero = Barbero.objects.get(pk=barbero_id, activo=True)
    except (ValueError, Barbero.DoesNotExist):
        return JsonResponse({'horas': []})

    # Horas ya ocupadas
    ocupadas = list(
        Cita.objects.filter(
            barbero=barbero,
            fecha=fecha,
            estado__in=[Cita.ESTADO_PENDIENTE, Cita.ESTADO_CONFIRMADA]
        ).values_list('hora', flat=True)
    )
    ocupadas_str = [h.strftime('%H:%M') for h in ocupadas]

    # Generar slots de 30 minutos de 8am a 8pm
    horas_disponibles = []
    for h in range(8, 20):
        for m in [0, 30]:
            t = time(h, m)
            t_str = t.strftime('%H:%M')
            if t_str not in ocupadas_str:
                horas_disponibles.append(t_str)

    return JsonResponse({'horas': horas_disponibles, 'ocupadas': ocupadas_str})
