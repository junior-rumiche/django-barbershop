from django.urls import path
from core.apps.backoffice.views.auth_views import (
    BackofficeLoginView,
    BackofficeLogoutView,
)

from core.apps.backoffice.views.dashboard_views import DashboardView


urlpatterns = [
    path("login/", BackofficeLoginView.as_view(), name="login"),
    path("logout/", BackofficeLogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
