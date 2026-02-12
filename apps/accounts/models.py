from django.db import models
from django.contrib.auth.models import User
import random
import string
from django.utils import timezone
from datetime import timedelta

class UserProfile(models.Model):
    CITIZEN_TYPE_CHOICES = [
        ('regular', 'Regular Citizen'),
        ('senior', 'Senior Citizen'),
        ('pwd', 'Person with Disability'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    citizen_type = models.CharField(max_length=20, choices=CITIZEN_TYPE_CHOICES, default='regular')
    contact_number = models.CharField(max_length=20, blank=True)
    id_number = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profile'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"
    
    def get_priority_level(self):
        if self.citizen_type == 'senior':
            return 1
        elif self.citizen_type == 'pwd':
            return 2
        return 3


class EmailVerificationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification_code')
    email = models.EmailField()
    verification_code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'email_verification_code'
    
    def __str__(self):
        return f"{self.email} - {self.verification_code}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        return not self.is_used and not self.is_expired()
    
    @staticmethod
    def generate_code():
        return ''.join(random.choices(string.digits, k=6))
    
    @staticmethod
    def create_verification_code(user, email):
        # Delete any existing code
        EmailVerificationCode.objects.filter(user=user).delete()
        
        code = EmailVerificationCode.generate_code()
        expires_at = timezone.now() + timedelta(minutes=10)
        
        verification = EmailVerificationCode.objects.create(
            user=user,
            email=email,
            verification_code=code,
            expires_at=expires_at
        )
        return verification
