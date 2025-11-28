from django.urls import path
from core.apps.backoffice.views.auth import BackofficeLoginView, BackofficeLogoutView


urlpatterns = [
    path("login/", BackofficeLoginView.as_view(), name="login"),
    path("logout/", BackofficeLogoutView.as_view(), name="logout"),
]
