#!/usr/bin/env python
"""
Test admin dashboard to identify 500 error
Run: python test_admin_dashboard_error.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from django.test import Client, override_settings
from django.contrib.auth.models import User

print("\n" + "="*60)
print("ADMIN DASHBOARD 500 ERROR DIAGNOSIS")
print("="*60)

with override_settings(ALLOWED_HOSTS=['*']):
    # Get an admin user
    admin = User.objects.filter(is_staff=True, is_superuser=True).first()
    
    if not admin:
        print("\n❌ No admin user found!")
        sys.exit(1)
    
    print(f"\nUsing admin user: {admin.username}")
    
    client = Client()
    client.login(username=admin.username, password='Admin@12345')
    
    # Test admin dashboard access
    print("\n1. Testing admin dashboard access...")
    try:
        response = client.get('/admin-panel/')
        print(f"   - Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✓ Admin dashboard loaded successfully")
        elif response.status_code == 500:
            print(f"   ❌ Server Error 500")
            
            # Try to find error details in response
            content = response.content.decode('utf-8', errors='ignore')
            
            if "Traceback" in content:
                print(f"\n   Error traceback found:")
                lines = content.split('<')
                for line in lines:
                    if 'Traceback' in line or 'Error' in line or 'Exception' in line:
                        print(f"   {line[:200]}")
        else:
            print(f"   - Status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exception during dashboard access: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test database queries directly
    print("\n2. Testing admin dashboard queries...")
    
    try:
        from apps.admin_management.models import VerificationRequest, AdminLog
        from apps.appointments.models import Appointment
        from apps.queues.models import Queue
        from django.db.models import Q
        
        print("\n   a) Query: Pending verifications...")
        pending_verifications = User.objects.filter(profile__is_verified=False).count()
        print(f"      ✓ Count: {pending_verifications}")
        
        print("\n   b) Query: Pending appointments...")
        pending_appointments = Appointment.objects.filter(status='pending').count()
        print(f"      ✓ Count: {pending_appointments}")
        
        print("\n   c) Query: Total users...")
        total_users = User.objects.filter(profile__isnull=False).count()
        print(f"      ✓ Count: {total_users}")
        
        print("\n   d) Query: Today queues...")
        today_queues = Queue.objects.filter(
            Q(status__in=['waiting', 'serving']) & ~Q(queue_number__startswith='W-')
        ).count()
        print(f"      ✓ Count: {today_queues}")
        
        print("\n   e) Query: Active walk-in queues...")
        active_walkin_queues = Queue.objects.filter(
            queue_number__startswith='W-',
            status__in=['waiting', 'serving']
        ).count()
        print(f"      ✓ Count: {active_walkin_queues}")
        
        print("\n   ✓ All queries executed successfully!")
        
    except Exception as e:
        print(f"   ❌ Query error: {str(e)}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
