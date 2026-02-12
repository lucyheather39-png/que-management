"""
Diagnostic test to check which template is being rendered for each admin page.
This will help identify if the wrong template is being used.
"""
import os
import django
from django.test import Client
from django.test.utils import override_settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.accounts.models import UserProfile

# Create test admin
admin_user, created = User.objects.get_or_create(
    username='diagnostic_admin',
    defaults={
        'email': 'diadmin@test.com',
        'is_staff': True,
        'is_superuser': True,
    }
)

if created:
    admin_user.set_password('Diag@123')
    admin_user.save()
    UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={'citizen_type': 'regular', 'is_verified': True}
    )

# Test with proper ALLOWED_HOSTS
with override_settings(ALLOWED_HOSTS=['*']):
    client = Client()
    login_success = client.login(username='diagnostic_admin', password='Diag@123')
    print(f"Login successful: {login_success}\n")
    
    pages = [
        ('/admin-panel/', 'Dashboard', 'admin/dashboard.html'),
        ('/admin-panel/verifications/pending/', 'Pending Verifications', 'admin/pending_verifications.html'),
        ('/admin-panel/appointments/pending/', 'Pending Appointments', 'admin/pending_appointments.html'),
        ('/admin-panel/queue/management/', 'Queue Management', 'admin/queue_management.html'),
        ('/admin-panel/users/', 'Users Management', 'admin/users_management.html'),
        ('/admin-panel/logs/', 'Activity Logs', 'admin/logs.html'),
        ('/admin-panel/admin/create/', 'Create Admin', 'admin/create_admin.html'),
        ('/admin-panel/walkin-queues/', 'Walk-in Queues', 'admin/walkin_queues.html'),
    ]
    
    print("="*80)
    print("TEMPLATE RENDERING DIAGNOSTIC TEST")
    print("="*80)
    
    for url, name, expected_template in pages:
        response = client.get(url)
        status = response.status_code
        
        # Get template names
        template_names = []
        if hasattr(response, 'template_name'):
            template_names = response.template_name if isinstance(response.template_name, list) else [response.template_name]
        elif hasattr(response, 'templates'):
            template_names = [t.name for t in response.templates if hasattr(t, 'name')]
        
        print(f"\n{name}")
        print(f"URL: {url}")
        print(f"Status: {status}")
        print(f"Expected template: {expected_template}")
        print(f"Actual templates: {template_names}")
        
        # Check content for specific identifying text
        content = response.content.decode() if status == 200 else ""
        if status == 200:
            # Check for page-specific content
            if name == "Pending Verifications" and "Pending User Verifications" in content:
                print("✓ Correct content found")
            elif name == "Pending Appointments" and ("Pending Appointments" in content or "Appointment" in content):
                print("✓ Correct content found")
            elif name == "Dashboard" and "Admin Dashboard" in content:
                print("✓ Correct content found")
            elif name == "Queue Management" and ("Queue Management" in content or "Queue Config" in content):
                print("✓ Correct content found")  
            elif name == "Users Management" and ("Users" in content or "User Management" in content):
                print("✓ Correct content found")
            elif name == "Activity Logs" and ("Activity" in content or "Log" in content):
                print("✓ Correct content found")
            elif name == "Create Admin" and ("Create Admin" in content or "Admin Account" in content):
                print("✓ Correct content found")
            elif name == "Walk-in Queues" and ("Walk-in" in content or "Walkin" in content):
                print("✓ Correct content found")
            else:
                print(f"⚠ Content check inconclusive - first 300 chars: {content[:300]}")
        else:
            print(f"✗ Status code {status}")
            
    print("\n" + "="*80)
