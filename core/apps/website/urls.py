from django.urls import path
from .views import WebsiteHomeView, WebsiteAboutView

urlpatterns = [
    path("", WebsiteHomeView.as_view(), name="home"),
    path("about/", WebsiteAboutView.as_view(), name="about"),
]
