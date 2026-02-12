from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField()
    service_type = models.CharField(max_length=100)
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    priority_level = models.IntegerField(default=3)
    is_senior_citizen = models.BooleanField(default=False)
    is_pwd = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_appointments')
    
    class Meta:
        db_table = 'appointment'
        ordering = ['-appointment_date']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['appointment_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Appointment - {self.user.get_full_name()} on {self.appointment_date.strftime('%Y-%m-%d %H:%M')}"
    
    def get_priority_label(self):
        if self.is_senior_citizen:
            return 'Senior Citizen'
        elif self.is_pwd:
            return 'PWD'
        return 'Regular'
    
    def get_status_display_value(self):
        status_map = {
            'pending': 'Pending Approval',
            'approved': 'Approved',
            'rejected': 'Rejected',
            'completed': 'Completed',
            'cancelled': 'Cancelled',
        }
        return status_map.get(self.status, self.status)
