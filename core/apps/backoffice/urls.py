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
from core.apps.backoffice.views.products import (
    ProductListView,
    ProductCreateView,
    ProductUpdateView,
)
from core.apps.backoffice.views.orders import (
    OrderListView,
    OrderCreateView,
    OrderUpdateView,
    OrderPrintView,
)
from core.apps.backoffice.views.supplies import (
    SupplyListView,
    SupplyCreateView,
    SupplyUpdateView,
)
from core.apps.backoffice.views.barbers import (
    BarberListView,
    BarberCreateView,
    BarberUpdateView,
    BarberUpdateView,
)
from core.apps.backoffice.views.appointments import (
    AppointmentListView,
    AppointmentCreateView,
    AppointmentUpdateView,
    AppointmentCalendarView,
    AppointmentJSONView,
)
from core.apps.backoffice.views.profile import ProfileUpdateView


urlpatterns = [
    path("login/", BackofficeLoginView.as_view(), name="login"),
    path("logout/", BackofficeLogoutView.as_view(), name="logout"),
    path("", DashboardView.as_view(), name="dashboard"),
    
    # Profile
    path("profile/", ProfileUpdateView.as_view(), name="user_profile"),

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

    # Products URLs (is_service=False)
    path("products/", ProductListView.as_view(), {"is_service": False}, name="product_list"),
    path("products/add/", ProductCreateView.as_view(), {"is_service": False}, name="product_add"),
    path("products/<int:pk>/edit/", ProductUpdateView.as_view(), {"is_service": False}, name="product_edit"),

    # Services URLs (is_service=True)
    path("services/", ProductListView.as_view(), {"is_service": True}, name="service_list"),
    path("services/add/", ProductCreateView.as_view(), {"is_service": True}, name="service_add"),
    path("services/<int:pk>/edit/", ProductUpdateView.as_view(), {"is_service": True}, name="service_edit"),

    # Orders URLs
    path("orders/", OrderListView.as_view(), name="order_list"),
    path("orders/add/", OrderCreateView.as_view(), name="order_add"),
    path("orders/<int:pk>/edit/", OrderUpdateView.as_view(), name="order_edit"),
    path("orders/<int:pk>/print/", OrderPrintView.as_view(), name="order_print"),

    # Supplies URLs
    path("supplies/", SupplyListView.as_view(), name="supply_list"),
    path("supplies/add/", SupplyCreateView.as_view(), name="supply_add"),
    path("supplies/<int:pk>/edit/", SupplyUpdateView.as_view(), name="supply_edit"),

    # Barbers URLs
    path("barbers/", BarberListView.as_view(), name="barber_list"),
    path("barbers/add/", BarberCreateView.as_view(), name="barber_add"),
    path("barbers/<int:pk>/edit/", BarberUpdateView.as_view(), name="barber_edit"),

    # Appointments URLs
    path("appointments/", AppointmentListView.as_view(), name="appointment_list"),
    path("appointments/calendar/", AppointmentCalendarView.as_view(), name="appointment_calendar"),
    path("api/appointments/events/", AppointmentJSONView.as_view(), name="appointment_events"),
    path("appointments/add/", AppointmentCreateView.as_view(), name="appointment_add"),
    path("appointments/<int:pk>/edit/", AppointmentUpdateView.as_view(), name="appointment_edit"),
]