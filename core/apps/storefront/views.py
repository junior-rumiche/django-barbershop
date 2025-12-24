from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta, time
import json

from core.apps.storefront.forms import PublicAppointmentForm
from core.apps.backoffice.models import Appointment, BarberProfile, WorkSchedule, Product, Order

class HomeView(TemplateView):
    template_name = "storefront/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass active barbers and services to the template for the initial render
        context['barbers'] = BarberProfile.objects.filter(is_active=True)
        # Only services (not products)
        context['services'] = Product.objects.filter(is_service=True, category__status=True) 
        return context


class BookingView(View):
    def post(self, request, *args, **kwargs):
        # We expect a standard POST form submission via AJAX
        form = PublicAppointmentForm(request.POST)
        if form.is_valid():
            try:
                appointment = form.save()
                return JsonResponse({
                    "success": True, 
                    "message": "Cita solicitada con éxito.",
                    "id": appointment.id
                })
            except Exception as e:
                return JsonResponse({"success": False, "message": str(e)}, status=400)
        else:
            errors = form.errors.as_json()
            return JsonResponse({"success": False, "message": "Datos inválidos", "errors": errors}, status=400)


def availability_api(request):
    """
    Returns available time slots for a specific barber and date.
    Query Params:
    - barber_id: int
    - date: YYYY-MM-DD
    """
    barber_id = request.GET.get('barber_id')
    date_str = request.GET.get('date')

    if not barber_id or not date_str:
        return JsonResponse({"error": "Faltan parámetros"}, status=400)

    try:
        query_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        # Verify date is not in the past
        if query_date < timezone.now().date():
             return JsonResponse({"slots": []}) # No slots in past
            
    except ValueError:
        return JsonResponse({"error": "Fecha inválida"}, status=400)

    # 1. Get Schedule for that day
    # Django Weekday: 0=Monday, 6=Sunday. Python: same.
    day_idx = query_date.weekday()
    
    schedule = WorkSchedule.objects.filter(barber_id=barber_id, day_of_week=day_idx).first()
    
    if not schedule:
        return JsonResponse({"slots": []}) # Barber doesn't work this day

    # 2. Get Existing Appointments
    existing_appts = Appointment.objects.filter(
        barber_id=barber_id, 
        date=query_date,
        status__in=['REQUESTED', 'CONFIRMED', 'COMPLETED'] # Ignore CANCELED
    ).order_by('start_time')

    # 3. Calculate Slots
    # Logic: 
    # - Start from StartHour
    # - Iterate in 30min chunks (or strictly by duration? simplified to 30min start slots)
    # - Check if slot overlaps with any existing appointment
    # - Check if slot overlaps with lunch
    
    slots = []
    
    # Calculate Buffers (2 hours after start, 2 hours before end)
    start_dt = datetime.combine(query_date, schedule.start_hour)
    end_dt = datetime.combine(query_date, schedule.end_hour)
    
    # 2-hour buffer logic
    # Start buffer: Only applies if it's the CURRENT DAY
    if query_date == timezone.now().date():
        current_time = start_dt + timedelta(hours=2)
    else:
        current_time = start_dt

    # End buffer: Always applies
    cutoff_time = end_dt - timedelta(hours=2)

    # Lunch times
    lunch_start = None
    lunch_end = None
    if schedule.lunch_start and schedule.lunch_end:
        lunch_start = datetime.combine(query_date, schedule.lunch_start)
        lunch_end = datetime.combine(query_date, schedule.lunch_end)

    while current_time + timedelta(minutes=30) <= cutoff_time:
        slot_start = current_time
        slot_end = current_time + timedelta(minutes=30) # Assuming min service is 30m for slot display
        
        is_available = True
        
        # Check Lunch Overlap
        if lunch_start and lunch_end:
            if not (slot_end <= lunch_start or slot_start >= lunch_end):
                is_available = False
        
        # Check Appointment Overlap
            # Add Order (Walk-in) Overlap Check
            # We need to fetch active orders for this barber on this day
            active_orders = Order.objects.filter(
                created_by=barber_id, # Assumes barber_id passed is ID of BarberProfile, need to get User.
                                      # Wait, availability_api gets valid 'barber_id' (BarberProfile PK).
                                      # We need to get the User associated with this BarberProfile.
            )
            # Fetching barber user first
            barber_profile = get_object_or_404(BarberProfile, pk=barber_id)
            orders = Order.objects.filter(
                created_by=barber_profile.user,
                status='PENDING',
                created_at__date=query_date
            ).prefetch_related('items__product')

            for order in orders:
                 duration = 0
                 for item in order.items.all():
                     if item.product.is_service:
                         duration += item.product.duration * item.quantity
                 
                 if duration > 0:
                     o_start = timezone.localtime(order.created_at)
                     o_end = o_start + timedelta(minutes=duration)
                     # Using naive datetimes for comparison with slot_start/slot_end which are datetime objects
                     # slot_start is naive (datetime.combine)
                     # We should make o_start/o_end naive or make slot_start aware.
                     # Since variables like 'current_time' are likely naive from datetime.combine(date, time)
                     # let's make order times naive with same date
                     
                     # Actually, order.created_at includes date.
                     # ensuring we compare apples to apples.
                     # slot_start contains query_date.
                     
                     # Simple check:
                     if slot_start < o_end.replace(tzinfo=None) and slot_end > o_start.replace(tzinfo=None):
                         is_available = False
                         
            if is_available:
                 for appt in existing_appts:
                    appt_start = datetime.combine(query_date, appt.start_time)
                    appt_end = datetime.combine(query_date, appt.end_time)
                    
                    # Strict overlap check
                    if slot_start < appt_end and slot_end > appt_start:
                        is_available = False
                        break
        
        if is_available:
             # Check if it's today and time has passed
             if query_date == timezone.now().date() and slot_start < datetime.now():
                 pass
             else:
                 slots.append(slot_start.strftime("%I:%M %p"))

        current_time += timedelta(minutes=30)

    return JsonResponse({"slots": slots})
