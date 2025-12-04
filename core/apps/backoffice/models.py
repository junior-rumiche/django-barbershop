"""
Models for the backoffice application.
This module defines the data structures used in the backoffice.
"""

from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


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
    """
    Represents a product or service offered by the business.
    """

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
    """
    Represents a customer order, which can be pending, paid, or canceled.
    It tracks the client's name, the user who created it, and its current status.
    """

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

        for item in self.items.all():
            if not item.product.is_service:
                item.product.stock_qty -= item.quantity
                item.product.save()

        self.status = "PAID"
        self.collected_by = user_who_collected
        self.paid_at = timezone.now()
        self.save()


class OrderItem(models.Model):
    """
    Representa un artículo individual dentro de una orden de venta.
    Almacena información sobre el producto, cantidad, precio unitario y subtotal
    para ese artículo específico en la orden.
    """

    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Item")
    quantity = models.IntegerField(default=1, verbose_name="Cantidad")
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Precio Unitario"
    )
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Subtotal"
    )

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class SupplyEntry(models.Model):
    """
    Representa una entrada de suministro para un producto.
    Registra cuándo y quién añadió un producto al inventario,
    así como la cantidad y el costo asociado.
    """

    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, verbose_name="Producto"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Registrado por",
    )
    quantity = models.PositiveIntegerField(verbose_name="Cantidad (Unidades)")
    unit_cost = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Costo Unitario"
    )
    supplier = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Proveedor"
    )
    date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Ingreso")

    class Meta:
        verbose_name = "Entrada de Insumo"
        verbose_name_plural = "Entradas de Inventario"

    def __str__(self):
        return f"{self.product.name} (+{self.quantity})"

    def save(self, *args, **kwargs):
        # Solo ejecutamos esto si es una entrada NUEVA
        if not self.pk:
            with transaction.atomic():
                # A. Recuperar datos actuales del producto
                # Bloqueamos la fila del producto para evitar condiciones de carrera
                # self.product.refresh_from_db() # Opcional si no usamos select_for_update
                
                current_stock = self.product.stock_qty
                current_cost = self.product.cost

                # B. Calcular Valor Total del Inventario Existente
                # (Ej: 10 unidades * 5 soles = 50 soles de valor)
                current_inventory_value = current_stock * current_cost

                # C. Calcular Valor Total de lo Nuevo
                # (Ej: 5 unidades * 6 soles = 30 soles de valor)
                new_entry_value = self.quantity * Decimal(self.unit_cost)

                # D. Nuevo Stock Total
                new_total_stock = current_stock + self.quantity

                # E. Calcular Nuevo Costo Promedio (Evitar división por cero)
                # (50 soles + 30 soles) / 15 unidades = 5.33 costo promedio
                if new_total_stock > 0:
                    new_average_cost = (current_inventory_value + new_entry_value) / new_total_stock
                else:
                    new_average_cost = self.unit_cost

                # Actualizar Producto
                self.product.stock_qty = new_total_stock
                self.product.cost = new_average_cost
                self.product.save(update_fields=['stock_qty', 'cost'])
                
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
