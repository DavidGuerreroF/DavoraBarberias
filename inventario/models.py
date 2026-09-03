from django.db import models


class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(
        CategoriaProducto, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='productos'
    )
    precio_compra = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    precio_venta = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5)
    unidad = models.CharField(max_length=30, default='unidad')
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def stock_bajo(self):
        return self.stock <= self.stock_minimo


class MovimientoInventario(models.Model):
    TIPO_ENTRADA = 'entrada'
    TIPO_SALIDA = 'salida'
    TIPO_AJUSTE = 'ajuste'

    TIPOS = [
        (TIPO_ENTRADA, 'Entrada'),
        (TIPO_SALIDA, 'Salida'),
        (TIPO_AJUSTE, 'Ajuste'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPOS)
    cantidad = models.IntegerField()
    stock_anterior = models.IntegerField()
    stock_nuevo = models.IntegerField()
    motivo = models.CharField(max_length=200, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto} ({self.cantidad})"
