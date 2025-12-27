"""
Models for the backoffice application.
This module defines the data structures used in the backoffice.
"""

from datetime import time, timedelta, date, datetime
from django.db import models, transaction, IntegrityError
from django.db.models import Sum
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from decimal import Decimal
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

    def update_totals(self):
        """
        Recalcula el total de la orden sumando los subtotales de los items.
        """
        total = self.items.aggregate(total=Sum('subtotal'))['total'] or 0
        self.total_amount = total
        self.save(update_fields=['total_amount'])

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
        self.order.update_totals()

    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)
        order.update_totals()


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


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('REQUESTED', 'Solicitud (Pendiente de Contacto)'), # Estado Inicial
        ('CONFIRMED', 'Confirmada (Cliente Contactado)'),   # Ya hablaste con él
        ('COMPLETED', 'Atendida'),
        ('CANCELED', 'Cancelada / No Contestó'),
    ]

    # Datos Cliente
    client_name = models.CharField(max_length=150, verbose_name="Nombre Cliente")
    client_phone = models.CharField(max_length=20, verbose_name="WhatsApp / Teléfono")

    # Datos Cita
    barber = models.ForeignKey('BarberProfile', on_delete=models.PROTECT, verbose_name="Barbero")
    services = models.ManyToManyField('Product', verbose_name="Servicios Solicitados")

    date = models.DateField(verbose_name="Fecha")
    start_time = models.TimeField(verbose_name="Hora Inicio")
    end_time = models.TimeField(verbose_name="Hora Fin") 
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Estimado")
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='REQUESTED', 
        verbose_name="Estado Actual"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Solicitud de Cita"
        verbose_name_plural = "Agenda de Solicitudes"
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.client_name} - {self.date} {self.start_time}"

    def clean(self):
        if self.status == 'CANCELED': return
        if not self.start_time or not self.end_time: return
        
        # Check overlaps
        overlapping = Appointment.objects.filter(
            barber=self.barber, date=self.date
        ).exclude(status='CANCELED').exclude(pk=self.pk).exclude(start_time__isnull=True).exclude(end_time__isnull=True)
        
        # Prepare self datetimes for comparison
        self_start_dt = datetime.combine(self.date, self.start_time)
        self_end_dt = datetime.combine(self.date, self.end_time)
        if self.end_time < self.start_time:
             self_end_dt += timedelta(days=1)

        for appt in overlapping:
            # Prepare overlapping appt datetimes
            appt_start_dt = datetime.combine(appt.date, appt.start_time)
            appt_end_dt = datetime.combine(appt.date, appt.end_time)
            if appt.end_time < appt.start_time:
                appt_end_dt += timedelta(days=1)

            # Strict overlap check using datetimes
            if self_start_dt < appt_end_dt and self_end_dt > appt_start_dt:
                raise ValidationError("El horario seleccionado ya no está disponible. Por favor elige otro.")

        # Check Work Schedule and Buffers
        if self.date and self.barber:
            day_idx = self.date.weekday()
            schedule = WorkSchedule.objects.filter(barber=self.barber, day_of_week=day_idx).first()

            if schedule:
                # 1. Base Schedule Times
                base_start_dt = datetime.combine(self.date, schedule.start_hour)
                base_end_dt = datetime.combine(self.date, schedule.end_hour)
                # Handle overnight shift (e.g. 22:00 to 02:00)
                if schedule.end_hour < schedule.start_hour:
                    base_end_dt += timedelta(days=1)

                # 2. Calculate Buffered Windows
                # Start Buffer: Lead Time logic (1 hour from NOW if today)
                # Use Local Time (Peru) for "Today" check
                now_local = timezone.localtime(timezone.now())
                
                if self.date == now_local.date():
                     # Minimum time is MAX(Shift Start, Now + 1h)
                     # Convert now_local to naive to compare with base_start_dt (which is naive from datetime.combine)
                     min_lead_time = now_local.replace(tzinfo=None) + timedelta(hours=1)
                     
                     if min_lead_time > base_start_dt:
                        valid_start_dt = min_lead_time
                     else:
                        valid_start_dt = base_start_dt
                else:
                     valid_start_dt = base_start_dt

                # End Buffer: Allow full shift usage
                valid_end_dt = base_end_dt
                
                # 3. Appointment Times to Datetime
                appt_start_dt = datetime.combine(self.date, self.start_time)
                appt_end_dt = datetime.combine(self.date, self.end_time)
                # Handle appointment crossing midnight
                if self.end_time < self.start_time:
                    appt_end_dt += timedelta(days=1)

                if appt_start_dt < valid_start_dt:
                    # Provide clear message depending on if it's shift start or lead time issue
                    # Re-calculate checks using local time variables
                    check_now_local = timezone.localtime(timezone.now())
                    min_lead_limit = check_now_local.replace(tzinfo=None) + timedelta(hours=1)
                    
                    if self.date == check_now_local.date() and min_lead_limit > base_start_dt:
                         raise ValidationError("Las citas deben reservarse con al menos 1 hora de anticipación.")
                    else:
                         formatted_start = valid_start_dt.strftime('%I:%M %p')
                         raise ValidationError(f"La cita debe estar dentro del horario laboral. Inicio válido desde: {formatted_start}")
                
                if appt_end_dt > valid_end_dt:
                    formatted_end = valid_end_dt.strftime('%I:%M %p')
                    raise ValidationError(f"La cita debe terminar dentro del horario laboral. Fin límite: {formatted_end}")
            else:
                raise ValidationError("El barbero no tiene horario asignado para este día.")

    def create_order(self, user):
        """
        Creates an Order from this Appointment.
        Expected user is the one triggering the action (backoffice staff).
        The Order 'created_by' will be the barber if mapped, or the trigger user.
        """
        if self.status != 'CONFIRMED':
             raise ValidationError("Solo citas CONFIRMADAS pueden convertirse en orden.")
        
        if not self.services.exists():
             raise ValidationError("La cita no tiene servicios asignados.")

        with transaction.atomic():
            # Determine creator (Barber's user > Trigger User)
            barber_user = self.barber.user if self.barber and self.barber.user else user
            
            order = Order.objects.create(
                created_by=barber_user, 
                client_name=self.client_name, # Map Client Name
                status='PENDING',
                total_amount=0 
            )

            total = 0
            for service in self.services.all():
                item = OrderItem.objects.create(
                    order=order,
                    product=service,
                    quantity=1,
                    unit_price=service.price,
                    subtotal=service.price
                )
                total += item.subtotal

            order.total_amount = total
            order.save()
            
            # Update Appointment Status
            self.status = 'COMPLETED'
            self.save()
            
            return order

        # Check Active Orders (Walk-ins)
        # We assume the barber user is the one who created the order
        if self.barber and self.barber.user:
            active_orders = Order.objects.filter(
                created_by=self.barber.user,
                status='PENDING',
                created_at__date=self.date 
            ).prefetch_related('items__product')
            
            for order in active_orders:
                # Calculate Duration
                duration_minutes = 0
                for item in order.items.all():
                    if item.product.is_service:
                        duration_minutes += item.product.duration * item.quantity
                
                if duration_minutes > 0:
                    # Order times are timezone aware usually, simplify for comparison
                    # Convert order time to local time if needed or just use time component
                    order_start = timezone.localtime(order.created_at).time()
                    order_end_dt = timezone.localtime(order.created_at) + timedelta(minutes=duration_minutes)
                    order_end = order_end_dt.time()
                    
                    # Handle day wrapping if needed (rare for barber hours but possible)
                    if order_end_dt.date() > timezone.localtime(order.created_at).date():
                        order_end = time(23, 59)

                    if self.start_time < order_end and self.end_time > order_start:
                         raise ValidationError("El barbero está ocupado con una atención en curso (Walk-in).")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)