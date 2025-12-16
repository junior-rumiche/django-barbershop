"""
Models for the backoffice application.
This module defines the data structures used in the backoffice.
"""

from django.db import models, transaction
from django.core.exceptions import ValidationError
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
    duration = models.PositiveIntegerField(
        default=30,
        verbose_name="Duración (min)",
        help_text="Tiempo estimado en minutos.",
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

    @transaction.atomic
    def mark_as_paid(self, user_who_collected):
        """
        Cierra la venta, valida stock y descuenta inventario.
        Si algo falla, la transacción atómica revierte todo.
        """
        if self.status == "PAID":
            return

        for item in self.items.all():
            if not item.product.is_service:
                product_locked = Product.objects.select_for_update().get(
                    pk=item.product.pk
                )

                if product_locked.stock_qty < item.quantity:
                    raise ValidationError(
                        f"Stock insuficiente para '{product_locked.name}'. "
                        f"Solicitado: {item.quantity}, Disponible: {product_locked.stock_qty}"
                    )

                product_locked.stock_qty -= item.quantity
                product_locked.save()

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
        if not self.pk:
            with transaction.atomic():
                locked_product = Product.objects.select_for_update().get(
                    pk=self.product.pk
                )

                current_stock = locked_product.stock_qty
                current_cost = locked_product.cost

                # B. Calcular Valor Total del Inventario Existente
                current_inventory_value = current_stock * current_cost

                # C. Calcular Valor Total de lo Nuevo
                new_entry_value = self.quantity * Decimal(self.unit_cost)

                # D. Nuevo Stock Total
                new_total_stock = current_stock + self.quantity

                # E. Calcular Nuevo Costo Promedio
                if new_total_stock > 0:
                    new_average_cost = (
                        current_inventory_value + new_entry_value
                    ) / new_total_stock
                else:
                    new_average_cost = self.unit_cost

                # Actualizar el producto BLOQUEADO
                locked_product.stock_qty = new_total_stock
                locked_product.cost = new_average_cost
                locked_product.save()  # Guardamos el producto actualizado

                # Finalmente guardamos la entrada (SupplyEntry)
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)


class BarberProfile(models.Model):
    """
    Convierte a un User en 'Barbero' con datos públicos.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="barber_profile"
    )
    nickname = models.CharField(max_length=50, verbose_name="Apodo", blank=True, null=True)
    photo = models.ImageField(upload_to="barbers/", blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Disponible en Web")

    class Meta:
        verbose_name = "Perfil de Barbero"
        verbose_name_plural = "Perfiles de Barberos"

    def __str__(self):
        if self.nickname:
             return self.nickname
        return self.user.get_full_name() or self.user.username


class WorkSchedule(models.Model):
    # Django usa 0=Lunes, 6=Domingo
    DAYS = [
        (0, "Lunes"),
        (1, "Martes"),
        (2, "Miércoles"),
        (3, "Jueves"),
        (4, "Viernes"),
        (5, "Sábado"),
        (6, "Domingo"),
    ]

    barber = models.ForeignKey(
        BarberProfile, related_name="schedules", on_delete=models.CASCADE
    )
    day_of_week = models.IntegerField(choices=DAYS, verbose_name="Día de la Semana")

    start_hour = models.TimeField(verbose_name="Hora Entrada")
    end_hour = models.TimeField(verbose_name="Hora Salida")
    lunch_start = models.TimeField(
        null=True, blank=True, verbose_name="Inicio Refrigerio"
    )
    lunch_end = models.TimeField(null=True, blank=True, verbose_name="Fin Refrigerio")

    class Meta:
        unique_together = ("barber", "day_of_week")
        verbose_name = "Horario Laboral"
        verbose_name_plural = "Horarios Laborales"
        ordering = ["day_of_week"]

    def __str__(self):
        return f"{self.barber} - {self.get_day_of_week_display()}"
