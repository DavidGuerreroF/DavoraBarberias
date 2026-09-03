from django.shortcuts import render
from .models import ConfiguracionBarberia
from servicios.models import Servicio
from barberos.models import Barbero


def home(request):
    config = ConfiguracionBarberia.get_config()
    servicios = Servicio.objects.filter(activo=True)[:6]
    barberos = Barbero.objects.filter(activo=True)
    context = {
        'config': config,
        'servicios': servicios,
        'barberos': barberos,
        'page': 'home',
    }
    return render(request, 'public/home.html', context)
