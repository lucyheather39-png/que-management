#!/usr/bin/env python
"""
Test dashboard view to identify the exact error
Run: python test_dashboard_error.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from django.test import Client, override_settings
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile

print("\n" + "="*60)
print("DASHBOARD ERROR DIAGNOSIS")
print("="*60)

with override_settings(ALLOWED_HOSTS=['*']):
    # Create a test user
    username = 'dashboard_test_user'
    user = User.objects.filter(username=username).first()
    
    if not user:
        print("\nCreating test user...")
        user = User.objects.create_user(
            username=username,
            email='dashboard@test.com',
            password='TestPass123'
        )
        profile = UserProfile.objects.create(
            user=user,
            citizen_type='regular',
            is_verified=True
        )
        print(f"✓ Created user: {username}")
    else:
        print(f"\nUsing existing user: {username}")
    
    client = Client()
    client.login(username=username, password='TestPass123')
    
    # Test dashboard access
    print("\n1. Testing dashboard access...")
    try:
        response = client.get('/queue/dashboard/')
        print(f"   - Status: {response.status_code}")
        
        # Check response content
        content = response.content.decode()
        
        if "Error loading some dashboard data" in content:
            print(f"   ❌ Error message shown on dashboard")
        else:
            print(f"   ✓ Dashboard loaded without error")
            
        # Check for specific error patterns
        if "Traceback" in content or "Internal Server Error" in content:
            print(f"   ⚠ Server error detected")
    except Exception as e:
        print(f"   ❌ Exception during dashboard access: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test database queries directly
    print("\n2. Testing database queries...")
    
    from django.utils import timezone
    from apps.queues.models import Queue
    from apps.appointments.models import Appointment
    
    try:
        print("\n   a) Queue query test...")
        user_queues = Queue.objects.filter(user=user, date=timezone.now().date())
        print(f"      ✓ Query successful: {user_queues.count()} queues found")
    except Exception as e:
        print(f"      ❌ Query failed: {str(e)}")
    
    try:
        print("\n   b) Appointments query test...")
        user_appointments = Appointment.objects.filter(
            user=user,
            status__in=['pending', 'approved']
        ).order_by('-created_at')[:5]
        print(f"      ✓ Query successful: {user_appointments.count()} appointments found")
    except Exception as e:
        print(f"      ❌ Query failed: {str(e)}")
    
    try:
        print("\n   c) Profile existence test...")
        profile = user.profile
        print(f"      ✓ Profile exists: {profile.citizen_type}")
    except Exception as e:
        print(f"      ❌ Profile error: {str(e)}")

print("\n" + "="*60)
