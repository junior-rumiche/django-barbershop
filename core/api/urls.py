from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.api.views import ServiceViewSet, UserViewSet, GroupViewSet

router = DefaultRouter()
router.register(r'services', ServiceViewSet)
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
