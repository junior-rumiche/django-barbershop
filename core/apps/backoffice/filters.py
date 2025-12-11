import django_filters
from django import forms
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User, Group
from core.apps.backoffice.models import Category, Product, Order, SupplyEntry


class SupplyEntryFilter(django_filters.FilterSet):
    keywords = django_filters.CharFilter(
        method="filter_keywords",
        label="Buscar",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Producto o proveedor..."}
        ),
    )
    date = django_filters.DateFromToRangeFilter(
        label="Fecha",
        widget=django_filters.widgets.RangeWidget(
            attrs={"class": "form-control", "placeholder": "YYYY-MM-DD"}
        ),
    )

    def filter_keywords(self, queryset, name, value):
        return queryset.filter(
            Q(product__name__icontains=value) | Q(supplier__icontains=value)
        )

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        if data is None:
            data = {}
            today = timezone.now().date()
            first_day = today.replace(day=1)
            data["date_after"] = first_day.strftime("%Y-%m-%d")
            data["date_before"] = today.strftime("%Y-%m-%d")
        else:
            data = data.copy()
            if "date_after" not in data and "date_before" not in data:
                today = timezone.now().date()
                first_day = today.replace(day=1)
                data["date_after"] = first_day.strftime("%Y-%m-%d")
                data["date_before"] = today.strftime("%Y-%m-%d")

        super().__init__(data, queryset, request=request, prefix=prefix)

    class Meta:
        model = SupplyEntry
        fields = ["keywords", "date"]


class OrderFilter(django_filters.FilterSet):
    created_by = django_filters.ModelChoiceFilter(
        queryset=User.objects.filter(is_active=True),
        label="Registrado por",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    client_name = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Cliente",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Buscar cliente..."}
        ),
    )
    status = django_filters.ChoiceFilter(
        choices=Order.STATUS_CHOICES,
        label="Estado",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    created_at = django_filters.DateFromToRangeFilter(
        label="Rango de Fechas",
        widget=django_filters.widgets.RangeWidget(
            attrs={"class": "form-control", "placeholder": "YYYY-MM-DD"}
        ),
    )

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        # Only apply defaults if no data is provided at all
        # This preserves the user's filter choices when paginating
        if data is None:
            data = {}
            today = timezone.now().strftime("%Y-%m-%d")
            data["created_at_after"] = today
            data["created_at_before"] = today
            data["status"] = "PENDING"
        else:
            # data is provided (from GET parameters), don't override it
            data = data.copy()

        super().__init__(data, queryset, request=request, prefix=prefix)

    class Meta:
        model = Order
        fields = ["created_by", "client_name", "status", "created_at"]


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Nombre",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Buscar por nombre..."}
        ),
    )
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.filter(status=True),
        label="Categoría",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    is_service = django_filters.BooleanFilter(
        label="Tipo",
        widget=forms.Select(
            attrs={"class": "form-select"},
            choices=[("", "Todos"), ("true", "Servicio"), ("false", "Producto")],
        ),
    )

    class Meta:
        model = Product
        fields = ["name", "category", "is_service"]


class CategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Nombre",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Buscar por nombre..."}
        ),
    )
    status = django_filters.BooleanFilter(
        label="Estado",
        widget=forms.Select(
            attrs={"class": "form-select"},
            choices=[("", "Todos"), ("true", "Activo"), ("false", "Inactivo")],
        ),
    )

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        if data is None:
            data = {"status": "true"}
        else:
            data = data.copy()
            if "status" not in data:
                data["status"] = "true"
        super().__init__(data, queryset, request=request, prefix=prefix)

    class Meta:
        model = Category
        fields = ["name", "status"]


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Usuario",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Buscar por usuario..."}
        ),
    )
    email = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Email",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Buscar por email..."}
        ),
    )
    is_active = django_filters.BooleanFilter(
        label="Estado",
        widget=forms.Select(
            attrs={"class": "form-select"},
            choices=[("", "Todos"), ("true", "Activo"), ("false", "Inactivo")],
        ),
    )

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        if data is None:
            data = {"is_active": "true"}
        else:
            data = data.copy()
            if "is_active" not in data:
                data["is_active"] = "true"
        super().__init__(data, queryset, request=request, prefix=prefix)

    class Meta:
        model = User
        fields = ["username", "email", "is_active"]


class GroupFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Nombre",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Buscar por nombre..."}
        ),
    )

    class Meta:
        model = Group
        fields = ["name"]
