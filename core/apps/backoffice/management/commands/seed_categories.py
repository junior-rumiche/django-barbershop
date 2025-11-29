from django.core.management.base import BaseCommand
from core.apps.backoffice.models import Category


class Command(BaseCommand):
    help = "Seed database with initial product categories"

    def handle(self, *args, **kwargs):
        categories = [
            {
                "name": "Cortes de Cabello",
                "description": "Estilos clásicos y modernos para todo tipo de cabello.",
                "status": True,
            },
            {
                "name": "Barba y Bigote",
                "description": "Perfilado, afeitado y cuidado de la barba.",
                "status": True,
            },
            {
                "name": "Cuidado Facial",
                "description": "Limpiezas, mascarillas y tratamientos relajantes.",
                "status": True,
            },
            {
                "name": "Productos Capilares",
                "description": "Ceras, geles, aceites y shampoos para el cuidado personal.",
                "status": True,
            },
            {
                "name": "Combos",
                "description": "Paquetes de servicios combinados a precio especial.",
                "status": True,
            },
        ]

        self.stdout.write("Iniciando carga de categorías...")

        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={
                    "description": cat_data["description"],
                    "status": cat_data["status"],
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Categoría creada: {category.name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"La categoría ya existe: {category.name}")
                )

        self.stdout.write(self.style.SUCCESS("¡Carga de categorías completada!"))
