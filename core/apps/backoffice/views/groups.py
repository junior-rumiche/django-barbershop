from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django_filters.views import FilterView
from django.contrib.auth.models import Group
from django.contrib import messages
from core.apps.backoffice.forms import GroupForm
from core.apps.backoffice.filters import GroupFilter
from core.mixins import BasePageMixin


class GroupListView(BasePageMixin, FilterView):
    model = Group
    template_name = "backoffice/groups/list.html"
    context_object_name = "groups"
    filterset_class = GroupFilter
    paginate_by = 10
    permission_required = "auth.view_group"
    page_title = "Lista de Grupos"

    def get_queryset(self):
        return Group.objects.all().order_by('name')


class GroupCreateView(BasePageMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = "backoffice/groups/form.html"
    success_url = reverse_lazy('backoffice:group_list')
    permission_required = "auth.add_group"
    page_title = "Crear Grupo"

    def form_valid(self, form):
        messages.success(self.request, "Grupo creado correctamente.")
        return super().form_valid(form)


class GroupUpdateView(BasePageMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = "backoffice/groups/form.html"
    success_url = reverse_lazy('backoffice:group_list')
    permission_required = "auth.change_group"
    page_title = "Editar Grupo"

    def form_valid(self, form):
        messages.success(self.request, "Grupo actualizado correctamente.")
        return super().form_valid(form)
