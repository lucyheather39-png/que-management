#!/usr/bin/env python
"""
Test admin dashboard with correct credentials
Run: python test_admin_dashboard_correct.py
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
print("ADMIN DASHBOARD WITH CORRECT CREDENTIALS")
print("="*60)

with override_settings(ALLOWED_HOSTS=['*']):
    client = Client()
    
    # Login with the correct admin user
    print(f"\n1. Logging in with admin user...")
    response = client.post('/auth/login/', {
        'username': 'admin',
        'password': 'Admin@12345'
    }, follow=False)
    
    print(f"   - Login status: {response.status_code}")
    print(f"   - Redirects to: {response.get('Location', 'No redirect')}")
    
    if '_auth_user_id' in client.session:
        print(f"   ✓ Session authenticated")
    
    # Access admin dashboard
    print(f"\n2. Accessing admin dashboard...")
    response = client.get('/admin-panel/', follow=False)
    print(f"   - Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✓ Dashboard loaded successfully")
    elif response.status_code in [301, 302]:
        print(f"   - Redirect to: {response.get('Location', 'Unknown')}")
    elif response.status_code == 500:
        print(f"   ❌ 500 Server Error")
        
        # Try to extract error info
        content = response.content.decode('utf-8', errors='ignore')
        if "Traceback" in content:
            # Find the error message
            import re
            match = re.search(r'<h3>([^<]+)</h3>', content)
            if match:
                print(f"   Error: {match.group(1)}")
    
    # Try to render template directly
    print(f"\n3. Checking template rendering...")
    try:
        from django.template.loader import render_to_string
        from django.contrib.auth.models import User as DjangoUser
        from django.db.models import Q
        from apps.appointments.models import Appointment
        from apps.queues.models import Queue
        
        # Simulate dashboard context
        pending_verifications = DjangoUser.objects.filter(profile__is_verified=False).count()
        pending_appointments = Appointment.objects.filter(status='pending').count()
        total_users = DjangoUser.objects.filter(profile__isnull=False).count()
        today_queues = Queue.objects.filter(
            Q(status__in=['waiting', 'serving']) & ~Q(queue_number__startswith='W-')
        ).count()
        active_walkin_queues = Queue.objects.filter(
            queue_number__startswith='W-',
            status__in=['waiting', 'serving']
        ).count()
        
        context = {
            'pending_verifications': pending_verifications,
            'pending_appointments': pending_appointments,
            'total_users': total_users,
            'today_queues': today_queues,
            'active_walkin_queues': active_walkin_queues,
        }
        
        html = render_to_string('pages/admin/dashboard.html', context)
        print(f"   ✓ Template rendered successfully ({len(html)} bytes)")
        
    except Exception as e:
        print(f"   ❌ Template rendering error: {str(e)}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
