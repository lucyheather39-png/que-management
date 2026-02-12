from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'appointment_date', 'status', 'get_priority_label', 'created_at')
    list_filter = ('status', 'appointment_date', 'is_senior_citizen', 'is_pwd')
    search_fields = ('user__username', 'user__email', 'purpose')
    readonly_fields = ('created_at', 'updated_at')
