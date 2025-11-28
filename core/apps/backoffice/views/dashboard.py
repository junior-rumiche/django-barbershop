from django.views.generic import TemplateView
from core.mixins import BasePageMixin


class DashboardView(BasePageMixin, TemplateView):
    template_name = "backoffice/dashboard.html"
    page_title = "Dashboard"
    permission_required = []
