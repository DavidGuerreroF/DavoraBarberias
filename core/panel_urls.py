from django.urls import path
from . import panel_views

urlpatterns = [
    # Auth
    path('login/', panel_views.panel_login, name='panel_login'),
    path('logout/', panel_views.panel_logout, name='panel_logout'),

    # Dashboard
    path('', panel_views.dashboard, name='panel_dashboard'),

    # Citas
    path('citas/', panel_views.citas_lista, name='panel_citas'),
    path('citas/nueva/', panel_views.cita_crear, name='panel_cita_crear'),
    path('citas/<int:pk>/editar/', panel_views.cita_editar, name='panel_cita_editar'),
    path('citas/<int:pk>/estado/', panel_views.cita_cambiar_estado, name='panel_cita_estado'),
    path('citas/<int:pk>/eliminar/', panel_views.cita_eliminar, name='panel_cita_eliminar'),

    # Barberos
    path('barberos/', panel_views.barberos_lista, name='panel_barberos'),
    path('barberos/nuevo/', panel_views.barbero_crear, name='panel_barbero_crear'),
    path('barberos/<int:pk>/editar/', panel_views.barbero_editar, name='panel_barbero_editar'),
    path('barberos/<int:pk>/eliminar/', panel_views.barbero_eliminar, name='panel_barbero_eliminar'),

    # Servicios
    path('servicios/', panel_views.servicios_lista, name='panel_servicios'),
    path('servicios/nuevo/', panel_views.servicio_crear, name='panel_servicio_crear'),
    path('servicios/<int:pk>/editar/', panel_views.servicio_editar, name='panel_servicio_editar'),
    path('servicios/<int:pk>/eliminar/', panel_views.servicio_eliminar, name='panel_servicio_eliminar'),

    # Clientes
    path('clientes/', panel_views.clientes_lista, name='panel_clientes'),
    path('clientes/nuevo/', panel_views.cliente_crear, name='panel_cliente_crear'),
    path('clientes/<int:pk>/editar/', panel_views.cliente_editar, name='panel_cliente_editar'),
    path('clientes/<int:pk>/eliminar/', panel_views.cliente_eliminar, name='panel_cliente_eliminar'),
]
