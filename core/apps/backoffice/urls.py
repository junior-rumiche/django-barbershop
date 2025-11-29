from django.urls import path
from core.apps.backoffice.views.auth import BackofficeLoginView, BackofficeLogoutView
from core.apps.backoffice.views.dashboard import DashboardView
from core.apps.backoffice.views.users import (
    UserListView,
    UserCreateView,
    UserUpdateView,
)
from core.apps.backoffice.views.groups import (
    GroupListView,
    GroupCreateView,
    GroupUpdateView,
)
from core.apps.backoffice.views.categories import (
    CategoryListView,
    CategoryCreateView,
    CategoryUpdateView,
)


urlpatterns = [
    path("login/", BackofficeLoginView.as_view(), name="login"),
    path("logout/", BackofficeLogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    
    # Users URLs
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/add/", UserCreateView.as_view(), name="user_add"),
    path("users/<int:pk>/edit/", UserUpdateView.as_view(), name="user_edit"),

    # Groups URLs
    path("groups/", GroupListView.as_view(), name="group_list"),
    path("groups/add/", GroupCreateView.as_view(), name="group_add"),
    path("groups/<int:pk>/edit/", GroupUpdateView.as_view(), name="group_edit"),

    # Categories URLs
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("categories/add/", CategoryCreateView.as_view(), name="category_add"),
    path("categories/<int:pk>/edit/", CategoryUpdateView.as_view(), name="category_edit"),
]