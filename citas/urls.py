from django.urls import path
from . import views

urlpatterns = [
    path('reservar/', views.reservar, name='reservar'),
    path('api/horas/', views.horas_disponibles, name='horas_disponibles'),
]
