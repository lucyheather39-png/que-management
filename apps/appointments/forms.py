from django import forms
from django.utils import timezone
from .models import Appointment
from apps.queues.models import Service

class AppointmentForm(forms.Form):
    appointment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
        }),
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'],
        label='Appointment Date & Time',
        help_text='Select a date and time in the future'
    )
    
    service_type = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True).order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Service Type',
        empty_label='-- Select a Service --'
    )
    
    purpose = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'What is the purpose of your appointment?'
        }),
        label='Purpose'
    )
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any additional information (optional)'
        }),
        label='Additional Notes (Optional)',
        required=False
    )
    
    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get('appointment_date')
        if appointment_date:
            # Make timezone aware if needed
            if timezone.is_naive(appointment_date):
                appointment_date = timezone.make_aware(appointment_date)
            
            if appointment_date <= timezone.now():
                raise forms.ValidationError('Appointment date must be at least 1 hour in the future.')
        return appointment_date
    
    def save_appointment(self, user):
        """Create and save appointment"""
        appointment = Appointment.objects.create(
            user=user,
            appointment_date=self.cleaned_data['appointment_date'],
            service_type=self.cleaned_data['service_type'].name,
            purpose=self.cleaned_data['purpose'],
            notes=self.cleaned_data.get('notes', ''),
            priority_level=user.profile.get_priority_level(),
            is_senior_citizen=user.profile.citizen_type == 'senior',
            is_pwd=user.profile.citizen_type == 'pwd',
        )
        return appointment
