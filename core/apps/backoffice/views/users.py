from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django_filters.views import FilterView
from django.contrib.auth.models import User
from django.contrib import messages
from core.apps.backoffice.forms import UserForm
from core.apps.backoffice.filters import UserFilter
from core.mixins import BasePageMixin


class UserListView(BasePageMixin, FilterView):
    model = User
    template_name = "backoffice/users/list.html"
    context_object_name = "users"
    filterset_class = UserFilter
    paginate_by = 10
    permission_required = "auth.view_user"
    page_title = "Lista de Usuarios"

    def get_queryset(self):
        return User.objects.all().order_by('-id')


class UserCreateView(BasePageMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = "backoffice/users/form.html"
    success_url = reverse_lazy('backoffice:user_list')
    permission_required = "auth.add_user"
    page_title = "Crear Usuario"

    def form_valid(self, form):
        messages.success(self.request, "Usuario creado correctamente.")
        return super().form_valid(form)


class UserUpdateView(BasePageMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = "backoffice/users/form.html"
    success_url = reverse_lazy('backoffice:user_list')
    permission_required = "auth.change_user"
    page_title = "Editar Usuario"

    def form_valid(self, form):
        messages.success(self.request, "Usuario actualizado correctamente.")
        return super().form_valid(form)
