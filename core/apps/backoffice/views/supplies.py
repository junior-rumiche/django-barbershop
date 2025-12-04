from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django.contrib import messages
from django.shortcuts import redirect
from django.db import transaction

from core.mixins import BasePageMixin
from core.apps.backoffice.models import SupplyEntry
from core.apps.backoffice.forms import SupplyEntryForm
from core.apps.backoffice.filters import SupplyEntryFilter


class SupplyListView(BasePageMixin, FilterView):
    model = SupplyEntry
    template_name = "backoffice/supplies/list.html"
    context_object_name = "supplies"
    filterset_class = SupplyEntryFilter
    paginate_by = 10
    page_title = "Entradas de Insumos"
    permission_required = "backoffice.view_supplyentry"

    def get_queryset(self):
        return SupplyEntry.objects.select_related("product", "created_by").order_by(
            "-date"
        )


class SupplyCreateView(BasePageMixin, CreateView):
    model = SupplyEntry
    form_class = SupplyEntryForm
    template_name = "backoffice/supplies/form.html"
    success_url = reverse_lazy("backoffice:supply_list")
    page_title = "Nueva Entrada"
    permission_required = "backoffice.add_supplyentry"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        try:
            with transaction.atomic():
                response = super().form_valid(form)
                messages.success(
                    self.request, "Entrada registrada y stock actualizado."
                )
                return response
        except Exception as e:
            form.add_error(None, f"Error al registrar la entrada: {e}")
            return self.form_invalid(form)


class SupplyUpdateView(BasePageMixin, UpdateView):
    model = SupplyEntry
    form_class = SupplyEntryForm
    template_name = "backoffice/supplies/form.html"
    success_url = reverse_lazy("backoffice:supply_list")
    page_title = "Editar Entrada"
    permission_required = "backoffice.change_supplyentry"

    def form_valid(self, form):
        messages.warning(
            self.request,
            "Entrada actualizada. Nota: El stock y costo del producto NO se han recalculado para evitar inconsistencias.",
        )
        return super().form_valid(form)
