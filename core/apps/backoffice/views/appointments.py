import json
from django.urls import reverse_lazy, reverse
from django.db.models import Sum, Q, F
from django.utils import timezone
from django.http import JsonResponse
from django.views.generic import (
    CreateView, UpdateView, ListView, DeleteView, DetailView, TemplateView, View
)
from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from core.mixins import BasePageMixin
from core.apps.backoffice.models import Appointment, BarberProfile, Product
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


class AppointmentCalendarView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'backoffice/appointments/calendar.html'
    permission_required = 'backoffice.view_appointment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Calendario de Citas'
        return context


class AppointmentJSONView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        start = request.GET.get('start')
        end = request.GET.get('end')
        
        # Parse ISO format from FullCalendar (YYYY-MM-DDTHH:mm:ss...)
        if start: start = start[:10]
        if end: end = end[:10]
        
        # Default range if not provided
        if not start or not end:
            today = timezone.now().date()
            start = today.replace(day=1)
            end = (today.replace(day=1) + timezone.timedelta(days=32)).replace(day=1)
        
        appointments = Appointment.objects.filter(
            date__range=[start, end]
        ).select_related('barber', 'barber__user')

        events = []
        for appt in appointments:
            # Color coding based on status
            color_class = 'bg-primary'
            if appt.status == 'REQUESTED':
                color_class = 'bg-warning'
            elif appt.status == 'COMPLETED':
                color_class = 'bg-success'
            elif appt.status == 'CANCELED':
                color_class = 'bg-danger'
            
            # Construct ISO datetime strings
            start_dt = f"{appt.date}T{appt.start_time}"
            end_dt = f"{appt.date}T{appt.end_time}"
            
            events.append({
                'id': appt.id,
                'title': f"{appt.client_name} - {appt.barber.nickname}",
                'start': start_dt,
                'end': end_dt,
                'className': color_class,
                'extendedProps': {
                    'status': appt.get_status_display(),
                    'phone': appt.client_phone,
                    'amount': str(appt.total_amount)
                }
            })
            
        return JsonResponse(events, safe=False)


class AppointmentCreateView(BasePageMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "backoffice/appointments/form.html"
    success_url = reverse_lazy("backoffice:appointment_list")
    page_title = "Nueva Cita"
    permission_required = "backoffice.add_appointment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        services = Product.objects.filter(is_service=True)
        services_data = {
            s.id: {'price': float(s.price), 'duration': s.duration} 
            for s in services
        }
        context['services_json'] = json.dumps(services_data)
        return context


class AppointmentUpdateView(BasePageMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "backoffice/appointments/form.html"
    success_url = reverse_lazy("backoffice:appointment_list")
    page_title = "Editar Cita"
    permission_required = "backoffice.change_appointment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        services = Product.objects.filter(is_service=True)
        services_data = {
            s.id: {'price': float(s.price), 'duration': s.duration} 
            for s in services
        }
        context['services_json'] = json.dumps(services_data)
        return context
