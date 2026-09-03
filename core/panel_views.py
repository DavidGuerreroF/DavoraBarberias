from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Q
from django.http import JsonResponse

from citas.models import Cita
from citas.forms import CitaAdminForm, BarberoForm, ServicioForm, ClienteForm
from barberos.models import Barbero
from servicios.models import Servicio
from clientes.models import Cliente
from core.models import ConfiguracionBarberia


# ─── AUTH ───────────────────────────────────────────────────────────────────

def panel_login(request):
    if request.user.is_authenticated:
        return redirect('panel_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'panel_dashboard'))
        messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'panel/login.html', {'page': 'login'})


@login_required
def panel_logout(request):
    logout(request)
    return redirect('home')


# ─── DASHBOARD ──────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    hoy = timezone.now().date()
    config = ConfiguracionBarberia.get_config()

    citas_hoy = Cita.objects.filter(fecha=hoy).order_by('hora')
    pendientes = Cita.objects.filter(estado=Cita.ESTADO_PENDIENTE).count()
    confirmadas_hoy = citas_hoy.filter(estado=Cita.ESTADO_CONFIRMADA).count()
    total_clientes = Cliente.objects.count()
    total_barberos = Barbero.objects.filter(activo=True).count()

    # Últimas citas
    ultimas_citas = Cita.objects.select_related('barbero', 'servicio').order_by('-creado')[:10]

    # Citas por estado hoy
    estados_hoy = {
        'pendiente': citas_hoy.filter(estado=Cita.ESTADO_PENDIENTE).count(),
        'confirmada': citas_hoy.filter(estado=Cita.ESTADO_CONFIRMADA).count(),
        'atendida': citas_hoy.filter(estado=Cita.ESTADO_ATENDIDA).count(),
        'cancelada': citas_hoy.filter(estado=Cita.ESTADO_CANCELADA).count(),
    }

    context = {
        'config': config,
        'hoy': hoy,
        'citas_hoy': citas_hoy,
        'pendientes': pendientes,
        'confirmadas_hoy': confirmadas_hoy,
        'total_clientes': total_clientes,
        'total_barberos': total_barberos,
        'ultimas_citas': ultimas_citas,
        'estados_hoy': estados_hoy,
        'page': 'dashboard',
    }
    return render(request, 'panel/dashboard.html', context)


# ─── CITAS ───────────────────────────────────────────────────────────────────

@login_required
def citas_lista(request):
    config = ConfiguracionBarberia.get_config()
    citas = Cita.objects.select_related('barbero', 'servicio').all()

    # Filtros
    estado = request.GET.get('estado', '')
    fecha = request.GET.get('fecha', '')
    barbero_id = request.GET.get('barbero', '')
    buscar = request.GET.get('q', '')

    if estado:
        citas = citas.filter(estado=estado)
    if fecha:
        citas = citas.filter(fecha=fecha)
    if barbero_id:
        citas = citas.filter(barbero_id=barbero_id)
    if buscar:
        citas = citas.filter(
            Q(nombre_cliente__icontains=buscar) |
            Q(whatsapp_cliente__icontains=buscar)
        )

    citas = citas.order_by('-fecha', '-hora')

    context = {
        'config': config,
        'citas': citas,
        'barberos': Barbero.objects.filter(activo=True),
        'estados': Cita.ESTADOS,
        'filtro_estado': estado,
        'filtro_fecha': fecha,
        'filtro_barbero': barbero_id,
        'filtro_q': buscar,
        'page': 'citas',
    }
    return render(request, 'panel/citas_lista.html', context)


@login_required
def cita_crear(request):
    config = ConfiguracionBarberia.get_config()
    if request.method == 'POST':
        form = CitaAdminForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cita creada correctamente.')
            return redirect('panel_citas')
    else:
        initial = {}
        if request.GET.get('fecha'):
            initial['fecha'] = request.GET.get('fecha')
        form = CitaAdminForm(initial=initial)
    return render(request, 'panel/cita_form.html', {
        'config': config, 'form': form, 'titulo': 'Nueva Cita', 'page': 'citas'
    })


@login_required
def cita_editar(request, pk):
    config = ConfiguracionBarberia.get_config()
    cita = get_object_or_404(Cita, pk=pk)
    if request.method == 'POST':
        form = CitaAdminForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cita actualizada.')
            return redirect('panel_citas')
    else:
        form = CitaAdminForm(instance=cita)
    return render(request, 'panel/cita_form.html', {
        'config': config, 'form': form, 'cita': cita,
        'titulo': 'Editar Cita', 'page': 'citas'
    })


@login_required
def cita_cambiar_estado(request, pk):
    """Cambio rápido de estado vía POST."""
    if request.method == 'POST':
        cita = get_object_or_404(Cita, pk=pk)
        nuevo_estado = request.POST.get('estado')
        estados_validos = [e[0] for e in Cita.ESTADOS]
        if nuevo_estado in estados_validos:
            cita.estado = nuevo_estado
            cita.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'ok': True,
                    'estado': cita.get_estado_display(),
                    'color': cita.color_estado
                })
            messages.success(request, f'Estado cambiado a: {cita.get_estado_display()}')
    return redirect('panel_citas')


@login_required
def cita_eliminar(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    if request.method == 'POST':
        cita.delete()
        messages.success(request, 'Cita eliminada.')
    return redirect('panel_citas')


# ─── BARBEROS ────────────────────────────────────────────────────────────────

@login_required
def barberos_lista(request):
    config = ConfiguracionBarberia.get_config()
    barberos = Barbero.objects.all()
    return render(request, 'panel/barberos_lista.html', {
        'config': config, 'barberos': barberos, 'page': 'barberos'
    })


@login_required
def barbero_crear(request):
    config = ConfiguracionBarberia.get_config()
    if request.method == 'POST':
        form = BarberoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Barbero agregado correctamente.')
            return redirect('panel_barberos')
    else:
        form = BarberoForm()
    return render(request, 'panel/barbero_form.html', {
        'config': config, 'form': form, 'titulo': 'Nuevo Barbero', 'page': 'barberos'
    })


@login_required
def barbero_editar(request, pk):
    config = ConfiguracionBarberia.get_config()
    barbero = get_object_or_404(Barbero, pk=pk)
    if request.method == 'POST':
        form = BarberoForm(request.POST, request.FILES, instance=barbero)
        if form.is_valid():
            form.save()
            messages.success(request, 'Barbero actualizado.')
            return redirect('panel_barberos')
    else:
        form = BarberoForm(instance=barbero)
    return render(request, 'panel/barbero_form.html', {
        'config': config, 'form': form, 'barbero': barbero,
        'titulo': 'Editar Barbero', 'page': 'barberos'
    })


@login_required
def barbero_eliminar(request, pk):
    barbero = get_object_or_404(Barbero, pk=pk)
    if request.method == 'POST':
        barbero.delete()
        messages.success(request, 'Barbero eliminado.')
    return redirect('panel_barberos')


# ─── SERVICIOS ───────────────────────────────────────────────────────────────

@login_required
def servicios_lista(request):
    config = ConfiguracionBarberia.get_config()
    servicios = Servicio.objects.all()
    return render(request, 'panel/servicios_lista.html', {
        'config': config, 'servicios': servicios, 'page': 'servicios'
    })


@login_required
def servicio_crear(request):
    config = ConfiguracionBarberia.get_config()
    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio creado.')
            return redirect('panel_servicios')
    else:
        form = ServicioForm()
    return render(request, 'panel/servicio_form.html', {
        'config': config, 'form': form, 'titulo': 'Nuevo Servicio', 'page': 'servicios'
    })


@login_required
def servicio_editar(request, pk):
    config = ConfiguracionBarberia.get_config()
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio actualizado.')
            return redirect('panel_servicios')
    else:
        form = ServicioForm(instance=servicio)
    return render(request, 'panel/servicio_form.html', {
        'config': config, 'form': form, 'servicio': servicio,
        'titulo': 'Editar Servicio', 'page': 'servicios'
    })


@login_required
def servicio_eliminar(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        servicio.delete()
        messages.success(request, 'Servicio eliminado.')
    return redirect('panel_servicios')


# ─── CLIENTES ────────────────────────────────────────────────────────────────

@login_required
def clientes_lista(request):
    config = ConfiguracionBarberia.get_config()
    clientes = Cliente.objects.all()
    buscar = request.GET.get('q', '')
    if buscar:
        clientes = clientes.filter(
            Q(nombre__icontains=buscar) |
            Q(apellido__icontains=buscar) |
            Q(whatsapp__icontains=buscar)
        )
    return render(request, 'panel/clientes_lista.html', {
        'config': config, 'clientes': clientes, 'buscar': buscar, 'page': 'clientes'
    })


@login_required
def cliente_crear(request):
    config = ConfiguracionBarberia.get_config()
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente registrado.')
            return redirect('panel_clientes')
    else:
        form = ClienteForm()
    return render(request, 'panel/cliente_form.html', {
        'config': config, 'form': form, 'titulo': 'Nuevo Cliente', 'page': 'clientes'
    })


@login_required
def cliente_editar(request, pk):
    config = ConfiguracionBarberia.get_config()
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado.')
            return redirect('panel_clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'panel/cliente_form.html', {
        'config': config, 'form': form, 'cliente': cliente,
        'titulo': 'Editar Cliente', 'page': 'clientes'
    })


@login_required
def cliente_eliminar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado.')
    return redirect('panel_clientes')
