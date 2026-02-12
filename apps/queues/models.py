from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Service(models.Model):
    SERVICE_TYPES = [
        ('birth', 'Birth Certificate'),
        ('death', 'Death Certificate'),
        ('marriage', 'Marriage Certificate'),
        ('permit', 'Business Permit'),
        ('assessment', 'Assessment'),
        ('other', 'Other Services'),
    ]
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    estimated_time = models.IntegerField(help_text="Estimated service time in minutes")
    max_daily_queue = models.IntegerField(default=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'service'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Queue(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('serving', 'Being Served'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='queues')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='queues')
    queue_number = models.CharField(max_length=20, unique=True)
    priority_level = models.IntegerField(default=3)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    position_in_queue = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    served_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    date = models.DateField(default=timezone.now)
    is_walkin = models.BooleanField(default=False, help_text='Walk-in customer without appointment')
    
    class Meta:
        db_table = 'queue'
        ordering = ['priority_level', 'created_at']
        indexes = [
            models.Index(fields=['date', 'service']),
            models.Index(fields=['status']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.queue_number} - {self.service.name}"
    
    def get_waiting_time(self):
        if self.status == 'completed':
            if self.completed_at and self.created_at:
                return (self.completed_at - self.created_at).total_seconds() / 60
        return None
    
    @property
    def priority_label(self):
        if self.priority_level == 1:
            return 'Senior Citizen'
        elif self.priority_level == 2:
            return 'PWD'
        return 'Regular'
