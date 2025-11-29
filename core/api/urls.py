from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.api.views import UserViewSet, GroupViewSet, CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
]