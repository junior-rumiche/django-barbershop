"""
Models for the backoffice application.
This module defines the data structures used in the backoffice.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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


class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pendiente de Pago"),
        ("PAID", "Pagado / Finalizado"),
        ("CANCELED", "Anulado"),
    ]

    client_name = models.CharField(max_length=150, verbose_name="Nombre del Cliente")

    created_by = models.ForeignKey(
        User,
        related_name="created_orders",
        on_delete=models.PROTECT,
        verbose_name="Registrado por",
    )

    collected_by = models.ForeignKey(
        User,
        related_name="collected_orders",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Cobrado por",
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )

    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Pago")

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="PENDING", verbose_name="Estado"
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Total"
    )

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        permissions = [
            ("can_print_order", "Puede imprimir orden"),
            ("can_mark_order_as_paid", "Puede marcar orden como pagada"),
        ]

    def __str__(self):
        return f"Cliente: {self.client_name} - ${self.total_amount}"

    def mark_as_paid(self, user_who_collected):
        """Función auxiliar para cerrar la venta limpiamente"""
        if self.status == "PAID":
            return

        # Descontar stock
        for item in self.items.all():
            if not item.product.is_service:
                item.product.stock_qty -= item.quantity
                item.product.save()

        self.status = "PAID"
        self.collected_by = user_who_collected
        self.paid_at = timezone.now()
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Item")
    quantity = models.IntegerField(default=1, verbose_name="Cantidad")

    # Guardamos el precio al momento de la venta por si cambia en el futuro
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Precio Unitario"
    )
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Subtotal"
    )

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
