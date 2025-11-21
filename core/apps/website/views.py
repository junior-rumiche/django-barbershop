from django.views.generic import TemplateView


class WebsiteHomeView(TemplateView):
    template_name = "website/home.html"


class WebsiteAboutView(TemplateView):
    template_name = "website/about.html"
