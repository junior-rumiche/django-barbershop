from rest_framework import viewsets, permissions, filters, status
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.core.exceptions import ValidationError
from django.core.exceptions import ValidationError
from core.apps.backoffice.models import Category, Product, Order, SupplyEntry, BarberProfile, Appointment, OrderItem
from core.api.serializers import (
    UserSerializer,
    GroupSerializer,
    CategorySerializer,
    ProductSerializer,
    OrderSerializer,
    SupplyEntrySerializer,
    BarberProfileSerializer,
    AppointmentSerializer,
)


class SupplyEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows supply entries to be viewed or edited.
    """

    queryset = SupplyEntry.objects.all().order_by("-date")
    serializer_class = SupplyEntrySerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = [filters.SearchFilter]
    search_fields = ["product__name", "supplier"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows orders to be viewed or edited.
    """

    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [permissions.DjangoModelPermissions]

    @action(detail=True, methods=["post"], url_path="mark-as-paid")
    def mark_as_paid(self, request, pk=None):
        order = self.get_object()

        if not request.user.has_perm("backoffice.can_mark_order_as_paid"):
            return Response(
                {"detail": "No tienes permiso para realizar esta acción."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if order.status == "PAID":
            return Response(
                {"detail": "La orden ya está pagada."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order.mark_as_paid(request.user)
            serializer = self.get_serializer(order)
            return Response(serializer.data)

        except ValidationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed or edited.
    """

    queryset = Product.objects.all().order_by("name")
    serializer_class = ProductSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows categories to be viewed or edited.
    """

    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.DjangoModelPermissions]


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-id")
    serializer_class = UserSerializer
    permission_classes = [permissions.DjangoModelPermissions]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [permissions.DjangoModelPermissions]


class BarberProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows barbers to be viewed or edited.
    """

    queryset = BarberProfile.objects.all().order_by("nickname")
    serializer_class = BarberProfileSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = [filters.SearchFilter]
    search_fields = ["nickname", "user__username", "user__first_name"]


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows appointments to be viewed or edited.
    """

    queryset = Appointment.objects.all().order_by("-date", "-start_time")
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = [filters.SearchFilter]
    filter_backends = [filters.SearchFilter]
    search_fields = ["client_name", "client_phone", "barber__nickname"]

    @action(detail=True, methods=["post"], url_path="convert-to-order")
    def convert_to_order(self, request, pk=None):
        appointment = self.get_object()

        try:
            order = appointment.create_order(request.user)
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
             return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
