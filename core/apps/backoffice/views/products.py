from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from core.mixins import BasePageMixin
from core.apps.backoffice.models import Product
from core.apps.backoffice.forms import ProductForm
from core.apps.backoffice.filters import ProductFilter


class ProductListView(BasePageMixin, FilterView):
    model = Product
    template_name = "backoffice/products/list.html"
    context_object_name = "products"
    filterset_class = ProductFilter
    paginate_by = 10
    permission_required = "backoffice.view_product"

    def get_queryset(self):
        is_service = self.kwargs.get("is_service", False)
        return (
            Product.objects.filter(is_service=is_service)
            .select_related("category")
            .order_by("name")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_service = self.kwargs.get("is_service", False)
        context["page_title"] = "Servicios" if is_service else "Productos"
        context["is_service"] = is_service
        return context


class ProductCreateView(BasePageMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "backoffice/products/form.html"
    permission_required = "backoffice.add_product"

    def get_initial(self):
        initial = super().get_initial()
        initial["is_service"] = self.kwargs.get("is_service", False)
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_service = self.kwargs.get("is_service", False)
        context["page_title"] = (
            "Nuevo Servicio" if is_service else "Nuevo Producto"
        )
        context["is_service"] = is_service
        return context

    def get_success_url(self):
        is_service = self.kwargs.get("is_service", False)
        return reverse_lazy(
            "backoffice:service_list" if is_service else "backoffice:product_list"
        )


class ProductUpdateView(BasePageMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "backoffice/products/form.html"
    permission_required = "backoffice.change_product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_service = self.kwargs.get("is_service", False)
        context["page_title"] = (
            "Editar Servicio" if is_service else "Editar Producto"
        )
        context["is_service"] = is_service
        return context

    def get_success_url(self):
        is_service = self.kwargs.get("is_service", False)
        return reverse_lazy(
            "backoffice:service_list" if is_service else "backoffice:product_list"
        )


class ProductDeleteView(BasePageMixin, DeleteView):
    model = Product
    template_name = "backoffice/products/delete.html"
    permission_required = "backoffice.delete_product"

    def get_success_url(self):
        is_service = self.kwargs.get("is_service", False)
        return reverse_lazy(
            "backoffice:service_list" if is_service else "backoffice:product_list"
        )