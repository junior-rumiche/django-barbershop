from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy


class BackofficeLoginView(LoginView):
    template_name = "backoffice/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("backoffice:dashboard")


class BackofficeLogoutView(LogoutView):
    template_name = "backoffice/logout.html"
    next_page = reverse_lazy("backoffice:login")
