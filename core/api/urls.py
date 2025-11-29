from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.api.views import UserViewSet, GroupViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]