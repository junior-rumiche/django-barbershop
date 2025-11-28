from django.urls import path
from core.apps.storefront.views import HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
]
