"""
Models for the backoffice application.
This module defines the data structures used in the backoffice.
"""

from django.db import models


class Category(models.Model):
    """
    Represents a product category.
    """

    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    status = models.BooleanField(default=True, verbose_name="Estado")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre del Producto/Servicio")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, verbose_name="Categoría"
    )

    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Precio de Venta"
    )
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Costo de Compra"
    )

    is_service = models.BooleanField(
        default=False,
        verbose_name="¿Es Servicio?",
        help_text="Marcar si es corte, barba, etc.",
    )
    stock_qty = models.IntegerField(default=0, verbose_name="Stock Actual")
    min_stock_alert = models.IntegerField(
        default=5, verbose_name="Alerta de Stock Mínimo"
    )

    class Meta:
        verbose_name = "Producto / Servicio"
        verbose_name_plural = "Productos y Servicios"

    def __str__(self):
        return f"{self.name} ({'Servicio' if self.is_service else 'Producto'})"
