from django.urls import path
from core.apps.storefront.views import HomeView, BookingView, availability_api

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("book/", BookingView.as_view(), name="booking_submit"),
    path("api/slots/", availability_api, name="availability_api"),
]
