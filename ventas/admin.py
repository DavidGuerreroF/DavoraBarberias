from django.contrib import admin
from .models import Venta, DetalleVenta


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['pk', 'cliente_nombre', 'barbero', 'total', 'metodo_pago', 'fecha']
    list_filter = ['metodo_pago', 'fecha', 'barbero']
    search_fields = ['cliente_nombre']
    inlines = [DetalleVentaInline]
    readonly_fields = ['fecha']


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ['venta', 'descripcion', 'cantidad', 'precio_unitario', 'subtotal']
