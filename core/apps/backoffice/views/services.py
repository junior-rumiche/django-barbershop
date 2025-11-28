from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from core.apps.backoffice.models import Service
from core.apps.backoffice.forms import ServiceForm
from core.mixins import BasePageMixin


class ServiceListView(BasePageMixin, ListView):
    model = Service
    template_name = "backoffice/services/list.html"
    context_object_name = "services"
    paginate_by = 10
    permission_required = "backoffice.view_service"
    page_title = "Lista de Servicios"

    def get_queryset(self):
        return Service.objects.all().order_by('-id')


class ServiceCreateView(BasePageMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = "backoffice/services/form.html"
    success_url = reverse_lazy('backoffice:service_list')
    permission_required = "backoffice.add_service"
    page_title = "Crear Servicio"

    def form_valid(self, form):
        messages.success(self.request, "Servicio creado correctamente.")
        return super().form_valid(form)


class ServiceUpdateView(BasePageMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = "backoffice/services/form.html"
    success_url = reverse_lazy('backoffice:service_list')
    permission_required = "backoffice.change_service"
    page_title = "Editar Servicio"

    def form_valid(self, form):
        messages.success(self.request, "Servicio actualizado correctamente.")
        return super().form_valid(form)


class ServiceDeleteView(BasePageMixin, DeleteView):
    model = Service
    template_name = "backoffice/services/delete.html"
    success_url = reverse_lazy('backoffice:service_list')
    permission_required = "backoffice.delete_service"
    page_title = "Eliminar Servicio"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Servicio eliminado correctamente.")
        return super().delete(request, *args, **kwargs)
