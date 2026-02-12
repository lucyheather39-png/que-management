from django.db import models
from django.contrib.auth.models import User

class VerificationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification_request')
    reason = models.TextField()
    attachment = models.FileField(upload_to='verifications/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_users')
    comments = models.TextField(blank=True)
    
    class Meta:
        db_table = 'verification_request'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Verification - {self.user.get_full_name()}"

class AdminLog(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_logs')
    action = models.CharField(max_length=200)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admin_log'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.admin.username} - {self.action}"
