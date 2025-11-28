from rest_framework import viewsets, permissions
from core.apps.backoffice.models import Service
from core.api.serializers import ServiceSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows services to be viewed or edited.
    """
    queryset = Service.objects.all().order_by('-id')
    serializer_class = ServiceSerializer
    permission_classes = [permissions.DjangoModelPermissions]
