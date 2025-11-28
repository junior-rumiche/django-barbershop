"""
Authentication views for the backoffice application.
Handles user login and logout functionalities.
"""

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy


class BackofficeLoginView(LoginView):
    """
    Custom LoginView for the backoffice.

    Uses a specific template and redirects authenticated users to the dashboard.
    Honors the 'next' URL parameter for redirection after successful login.
    """

    template_name = "backoffice/login.html"
    redirect_authenticated_user = True


class BackofficeLogoutView(LogoutView):
    """
    Custom LogoutView for the backoffice.

    Uses a specific template and redirects users to the backoffice login page
    after logging out.
    """

    template_name = "backoffice/logout.html"
    next_page = reverse_lazy("backoffice:login")
