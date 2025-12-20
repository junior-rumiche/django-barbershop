from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django_filters.views import FilterView
from core.mixins import BasePageMixin
from core.apps.backoffice.models import Appointment
from core.apps.backoffice.forms import AppointmentForm
from core.apps.backoffice.filters import AppointmentFilter


class AppointmentListView(BasePageMixin, FilterView):
    model = Appointment
    template_name = "backoffice/appointments/list.html"
    context_object_name = "appointments"
    filterset_class = AppointmentFilter
    paginate_by = 10
    page_title = "Agenda de Citas"
    permission_required = "backoffice.view_appointment"

    def get_queryset(self):
        return Appointment.objects.all().order_by("-date", "start_time")


class AppointmentCreateView(BasePageMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "backoffice/appointments/form.html"
    success_url = reverse_lazy("backoffice:appointment_list")
    page_title = "Nueva Cita"
    permission_required = "backoffice.add_appointment"


class AppointmentUpdateView(BasePageMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "backoffice/appointments/form.html"
    success_url = reverse_lazy("backoffice:appointment_list")
    page_title = "Editar Cita"
    permission_required = "backoffice.change_appointment"
