from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.api.views import (
    UserViewSet,
    GroupViewSet,
    CategoryViewSet,
    ProductViewSet,
    OrderViewSet,
    SupplyEntryViewSet,
    BarberProfileViewSet,
    AppointmentViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'supplies', SupplyEntryViewSet)
router.register(r'barbers', BarberProfileViewSet)
router.register(r'appointments', AppointmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]