from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django_filters.views import FilterView
from core.mixins import BasePageMixin
from core.apps.backoffice.models import BarberProfile
from core.apps.backoffice.forms import BarberProfileForm, WorkScheduleFormSet
from core.apps.backoffice.filters import BarberProfileFilter


class BarberListView(BasePageMixin, FilterView):
    model = BarberProfile
    template_name = "backoffice/barbers/list.html"
    context_object_name = "barbers"
    filterset_class = BarberProfileFilter
    paginate_by = 10
    page_title = "Barberos"
    permission_required = "backoffice.view_barberprofile"

    def get_queryset(self):
        return BarberProfile.objects.all().order_by("nickname")


class BarberCreateView(BasePageMixin, CreateView):
    model = BarberProfile
    form_class = BarberProfileForm
    template_name = "backoffice/barbers/form.html"
    success_url = reverse_lazy("backoffice:barber_list")
    page_title = "Nuevo Barbero"
    permission_required = "backoffice.add_barberprofile"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["schedules"] = WorkScheduleFormSet(self.request.POST)
        else:
            data["schedules"] = WorkScheduleFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        schedules = context["schedules"]
        self.object = form.save()
        if schedules.is_valid():
            schedules.instance = self.object
            schedules.save()
        else:
            # If formset is invalid, re-render form with errors
            return self.render_to_response(self.get_context_data(form=form))
        return super().form_valid(form)


class BarberUpdateView(BasePageMixin, UpdateView):
    model = BarberProfile
    form_class = BarberProfileForm
    template_name = "backoffice/barbers/form.html"
    success_url = reverse_lazy("backoffice:barber_list")
    page_title = "Editar Barbero"
    permission_required = "backoffice.change_barberprofile"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["schedules"] = WorkScheduleFormSet(self.request.POST, instance=self.object)
        else:
            data["schedules"] = WorkScheduleFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        schedules = context["schedules"]
        self.object = form.save()
        if schedules.is_valid():
            schedules.instance = self.object
            schedules.save()
        else:
             return self.render_to_response(self.get_context_data(form=form))
        return super().form_valid(form)
