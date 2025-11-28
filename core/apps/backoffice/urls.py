from django.urls import path
from core.apps.backoffice.views.auth import BackofficeLoginView, BackofficeLogoutView
from core.apps.backoffice.views.dashboard import DashboardView


urlpatterns = [
    path("login/", BackofficeLoginView.as_view(), name="login"),
    path("logout/", BackofficeLogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
