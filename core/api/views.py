from rest_framework import viewsets, permissions
from django.contrib.auth.models import User, Group
from core.apps.backoffice.models import Service
from core.api.serializers import ServiceSerializer, UserSerializer, GroupSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows services to be viewed or edited.
    """
    queryset = Service.objects.all().order_by('-id')
    serializer_class = ServiceSerializer
    permission_classes = [permissions.DjangoModelPermissions]


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer
    permission_classes = [permissions.DjangoModelPermissions]

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.DjangoModelPermissions]
