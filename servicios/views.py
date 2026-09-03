from django.shortcuts import render
from .models import Servicio
from core.models import ConfiguracionBarberia


def lista_servicios(request):
    config = ConfiguracionBarberia.get_config()
    servicios = Servicio.objects.filter(activo=True)
    return render(request, 'public/servicios.html', {
        'config': config,
        'servicios': servicios,
        'page': 'servicios',
    })
