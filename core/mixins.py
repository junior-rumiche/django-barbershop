from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class BasePageMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """
    Mixin general para manejar contexto de página y permisos.
    """

    page_title = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        return context
