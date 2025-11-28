from django.urls import path
from core.apps.backoffice.views.auth import BackofficeLoginView, BackofficeLogoutView
from core.apps.backoffice.views.dashboard import DashboardView
from core.apps.backoffice.views.services import (
    ServiceListView,
    ServiceCreateView,
    ServiceUpdateView,
    ServiceDeleteView,
)
from core.apps.backoffice.views.users import (
    UserListView,
    UserCreateView,
    UserUpdateView,
)


urlpatterns = [
    path("login/", BackofficeLoginView.as_view(), name="login"),
    path("logout/", BackofficeLogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    
    # Services URLs
    path("services/", ServiceListView.as_view(), name="service_list"),
    path("services/add/", ServiceCreateView.as_view(), name="service_add"),
    path("services/<int:pk>/edit/", ServiceUpdateView.as_view(), name="service_edit"),
    path("services/<int:pk>/delete/", ServiceDeleteView.as_view(), name="service_delete"),
    
    # Users URLs
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/add/", UserCreateView.as_view(), name="user_add"),
    path("users/<int:pk>/edit/", UserUpdateView.as_view(), name="user_edit"),
]
