from django.shortcuts import render
from .models import Barbero
from core.models import ConfiguracionBarberia


def lista_barberos(request):
    config = ConfiguracionBarberia.get_config()
    barberos = Barbero.objects.filter(activo=True)
    return render(request, 'public/barberos.html', {
        'config': config,
        'barberos': barberos,
        'page': 'barberos',
    })
