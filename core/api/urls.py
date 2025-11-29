from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.api.views import (
    UserViewSet,
    GroupViewSet,
    CategoryViewSet,
    ProductViewSet,
    OrderViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]