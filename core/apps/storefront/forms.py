from django import forms
from core.apps.backoffice.models import Appointment, Product, BarberProfile
from datetime import datetime, timedelta

class PublicAppointmentForm(forms.ModelForm):
    start_time = forms.TimeField(
        input_formats=["%H:%M", "%I:%M %p", "%I:%M%p"],
        required=True
    )
    
    class Meta:
        model = Appointment
        fields = [
            "client_name",
            "client_phone",
            "barber",
            "services",
            "date",
            "start_time",
        ]

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # 1. Default Status
        instance.status = 'REQUESTED'
        
        # 2. Calculate Total & Duration
        total = 0
        duration_minutes = 0
        
        # We need to save m2m after saving instance if commit=True
        # But for calculation we need access to services. 
        # Since this is a ModelForm, 'services' is in cleaned_data
        
        services = self.cleaned_data.get('services', [])
        for svc in services:
            total += svc.price
            duration_minutes += svc.duration
            
        instance.total_amount = total
        
        # 3. Calculate End Time
        # Combine date and start_time to make a full datetime for calculation if needed, 
        # but here we just need time math.
        
        if instance.start_time:
            # Create a dummy datetime to add duration
            dummy_date = datetime.combine(datetime.today(), instance.start_time)
            end_date = dummy_date + timedelta(minutes=duration_minutes)
            instance.end_time = end_date.time()
            
        if commit:
            instance.save()
            self.save_m2m() # Important for services
            
        return instance
