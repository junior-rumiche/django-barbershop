from django.core.management.base import BaseCommand
from core.apps.backoffice.models import Category, Product
from decimal import Decimal


class Command(BaseCommand):
    help = "Seed database with initial products and services"

    def handle(self, *args, **kwargs):
        # Define products with their associated category names
        products_data = [
            # Servicios (Cortes)
            {
                "name": "Corte Clásico",
                "category_name": "Cortes de Cabello",
                "price": "25.00",
                "cost": "0.00",
                "stock_qty": 0,
                "is_service": True,
            },
            {
                "name": "Corte Fade / Degradado",
                "category_name": "Cortes de Cabello",
                "price": "30.00",
                "cost": "0.00",
                "stock_qty": 0,
                "is_service": True,
            },
            {
                "name": "Corte Infantil",
                "category_name": "Cortes de Cabello",
                "price": "20.00",
                "cost": "0.00",
                "stock_qty": 0,
                "is_service": True,
            },
            # Servicios (Barba)
            {
                "name": "Perfilado de Barba",
                "category_name": "Barba y Bigote",
                "price": "15.00",
                "cost": "0.00",
                "stock_qty": 0,
                "is_service": True,
            },
            {
                "name": "Afeitado Completo (Toalla Caliente)",
                "category_name": "Barba y Bigote",
                "price": "25.00",
                "cost": "5.00", # Costo estimado de insumos
                "stock_qty": 0,
                "is_service": True,
            },
            # Servicios (Facial)
            {
                "name": "Limpieza Facial Express",
                "category_name": "Cuidado Facial",
                "price": "35.00",
                "cost": "8.00",
                "stock_qty": 0,
                "is_service": True,
            },
            {
                "name": "Black Mask",
                "category_name": "Cuidado Facial",
                "price": "20.00",
                "cost": "5.00",
                "stock_qty": 0,
                "is_service": True,
            },
            # Productos (Venta)
            {
                "name": "Cera Mate Strong Hold",
                "category_name": "Productos Capilares",
                "price": "45.00",
                "cost": "25.00",
                "stock_qty": 50,
                "is_service": False,
            },
            {
                "name": "Pomada Brillo Medio",
                "category_name": "Productos Capilares",
                "price": "40.00",
                "cost": "20.00",
                "stock_qty": 35,
                "is_service": False,
            },
            {
                "name": "Aceite para Barba (30ml)",
                "category_name": "Barba y Bigote",
                "price": "35.00",
                "cost": "18.00",
                "stock_qty": 20,
                "is_service": False,
            },
            {
                "name": "Shampoo Anticaspa",
                "category_name": "Productos Capilares",
                "price": "28.00",
                "cost": "14.00",
                "stock_qty": 15,
                "is_service": False,
            },
            # Combos
            {
                "name": "Combo Ejecutivo (Corte + Barba)",
                "category_name": "Combos",
                "price": "40.00",
                "cost": "5.00",
                "stock_qty": 0,
                "is_service": True,
            },
        ]

        self.stdout.write("Iniciando carga de productos y servicios...")

        for prod_data in products_data:
            category_name = prod_data.pop("category_name")
            try:
                category = Category.objects.get(name=category_name)
            except Category.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Categoría '{category_name}' no encontrada. Saltando producto '{prod_data['name']}'."
                    )
                )
                continue

            product, created = Product.objects.get_or_create(
                name=prod_data["name"],
                defaults={
                    "category": category,
                    "price": Decimal(prod_data["price"]),
                    "cost": Decimal(prod_data["cost"]),
                    "stock_qty": prod_data["stock_qty"],
                    "is_service": prod_data["is_service"],
                    "min_stock_alert": 5, # Default
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Producto creado: {product.name}")
                )
            else:
                # Update existing product
                product.category = category
                product.price = Decimal(prod_data["price"])
                product.cost = Decimal(prod_data["cost"])
                product.stock_qty = prod_data["stock_qty"]
                product.is_service = prod_data["is_service"]
                product.save()
                self.stdout.write(
                    self.style.WARNING(f"Producto actualizado: {product.name}")
                )

        self.stdout.write(self.style.SUCCESS("¡Carga de productos completada!"))