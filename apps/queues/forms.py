from django import forms
from .models import Queue, Service

class QueueCreationForm(forms.Form):
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True).order_by('name'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_service'
        }),
        label='Select Service',
        empty_label='-- Choose a Service --'
    )

class ServiceCreationForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'code', 'description', 'service_type', 'estimated_time', 'max_daily_queue', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter service name',
                'required': True
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter service code (e.g., BIRTH)',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter service description',
                'rows': 4,
                'required': True
            }),
            'service_type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'estimated_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estimated time in minutes',
                'type': 'number',
                'min': '1',
                'required': True
            }),
            'max_daily_queue': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maximum daily queue (default: 50)',
                'type': 'number',
                'min': '1',
                'value': '50'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'name': 'Service Name',
            'code': 'Service Code',
            'description': 'Description',
            'service_type': 'Service Type',
            'estimated_time': 'Estimated Time (minutes)',
            'max_daily_queue': 'Maximum Daily Queue',
            'is_active': 'Active Service',
        }
