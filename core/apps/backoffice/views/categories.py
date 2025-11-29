from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from core.mixins import BasePageMixin
from core.apps.backoffice.models import Category
from core.apps.backoffice.forms import CategoryForm
from core.apps.backoffice.filters import CategoryFilter


class CategoryListView(BasePageMixin, FilterView):
    model = Category
    template_name = "backoffice/categories/list.html"
    context_object_name = "categories"
    filterset_class = CategoryFilter
    paginate_by = 10
    page_title = "Categorías"
    permission_required = "backoffice.view_category"

    def get_queryset(self):
        return Category.objects.all().order_by("name")


class CategoryCreateView(BasePageMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "backoffice/categories/form.html"
    success_url = reverse_lazy("backoffice:category_list")
    page_title = "Nueva Categoría"
    permission_required = "backoffice.add_category"


class CategoryUpdateView(BasePageMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "backoffice/categories/form.html"
    success_url = reverse_lazy("backoffice:category_list")
    page_title = "Editar Categoría"
    permission_required = "backoffice.change_category"


class CategoryDeleteView(BasePageMixin, DeleteView):
    model = Category
    template_name = "backoffice/categories/delete.html"
    success_url = reverse_lazy("backoffice:category_list")
    permission_required = "backoffice.delete_category"
