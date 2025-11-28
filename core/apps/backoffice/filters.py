import django_filters
from django import forms
from django.contrib.auth.models import User
from core.apps.backoffice.models import Service

class ServiceFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por nombre...'})
    )
    status = django_filters.BooleanFilter(
        label='Estado',
        widget=forms.Select(attrs={'class': 'form-select'}, choices=[('', 'Todos'), ('true', 'Activo'), ('false', 'Inactivo')])
    )
    min_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        label='Precio Mínimo',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    max_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        label='Precio Máximo',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        if data is None:
            data = {'status': 'true'}
        else:
            data = data.copy()
            if 'status' not in data:
                data['status'] = 'true'
        super().__init__(data, queryset, request=request, prefix=prefix)

    class Meta:
        model = Service
        fields = ['name', 'status', 'min_price', 'max_price']


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por usuario...'})
    )
    email = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Email',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por email...'})
    )
    is_active = django_filters.BooleanFilter(
        label='Estado',
        widget=forms.Select(attrs={'class': 'form-select'}, choices=[('', 'Todos'), ('true', 'Activo'), ('false', 'Inactivo')])
    )

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        if data is None:
            data = {'is_active': 'true'}
        else:
            data = data.copy()
            if 'is_active' not in data:
                data['is_active'] = 'true'
        super().__init__(data, queryset, request=request, prefix=prefix)

    class Meta:
        model = User
        fields = ['username', 'email', 'is_active']