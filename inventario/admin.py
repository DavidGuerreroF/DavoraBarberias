from django.contrib import admin
from .models import CategoriaProducto, Producto, MovimientoInventario


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'stock', 'stock_minimo', 'precio_venta', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['nombre']
    list_editable = ['stock', 'precio_venta', 'activo']


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ['producto', 'tipo', 'cantidad', 'stock_anterior', 'stock_nuevo', 'fecha']
    list_filter = ['tipo', 'fecha']
    readonly_fields = ['fecha']
