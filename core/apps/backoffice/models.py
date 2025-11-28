"""
Models for the backoffice application.
This module defines the data structures used in the backoffice, starting with the Service model.
"""

from django.db import models


class Service(models.Model):
    """
    Represents a service offered by the barbershop.

    Attributes:
        name (str): The name of the service (e.g., 'Haircut', 'Shave'). Unique.
        description (str): A detailed description of what the service entails. Optional.
        price (Decimal): The cost of the service.
        status (bool): Indicates if the service is currently active/available. Defaults to True.
    """

    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    status = models.BooleanField(default=True, verbose_name="Estado")

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"

    def __str__(self):
        return self.name

    def apply_discount(self, percentage):
        """
        Calculates the price after applying a discount percentage.

        Args:
            percentage (float): The discount percentage (e.g., 10 for 10%).

        Returns:
            Decimal: The discounted price.
        """
        from decimal import Decimal

        discount_factor = Decimal(1) - (Decimal(percentage) / Decimal(100))
        return self.price * discount_factor

    def toggle_status(self):
        """
        Toggles the active status of the service and saves the change.
        """
        self.status = not self.status
        self.save()
