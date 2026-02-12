import os
import django
from django.test import Client
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.accounts.models import UserProfile

# Create test admin
admin_user, created = User.objects.get_or_create(
    username='test_admin_nav',
    defaults={
        'email': 'testadmin_nav@test.com',
        'is_staff': True,
        'is_superuser': True,
    }
)

if created:
    admin_user.set_password('TestAdmin@123')
    admin_user.save()
    UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={'citizen_type': 'regular', 'is_verified': True}
    )

# Login
client = Client()
login_success = client.login(username='test_admin_nav', password='TestAdmin@123')
print(f"Login success: {login_success}\n")

# Test pages
pages = [
    ('/admin-panel/', 'Dashboard'),
    ('/admin-panel/verifications/pending/', 'Pending Verifications'),
    ('/admin-panel/appointments/pending/', 'Pending Appointments'),
    ('/admin-panel/queue/management/', 'Queue Management'),
    ('/admin-panel/users/', 'Users Management'),
    ('/admin-panel/logs/', 'Activity Logs'),
    ('/admin-panel/admin/create/', 'Create Admin'),
    ('/admin-panel/walkin-queues/', 'Walk-in Queues'),
]

print("=" * 80)
print("Testing Admin Page Navigation")
print("=" * 80)

for url, name in pages:
    response = client.get(url, follow=True)
    print(f"\n{name}")
    print(f"URL: {url}")
    print(f"Status: {response.status_code}")
    print(f"Final URL: {response.request['PATH_INFO']}")
    print(f"Template used: {response.template_name if hasattr(response, 'template_name') else 'N/A'}")
    if response.status_code == 200:
        # Check if we're on the right page
        content = response.content.decode()
        if 'Admin Dashboard' in content or name in content:
            print(f"✓ Page loaded correctly")
        else:
            print(f"✗ WARNING: Expected content not found")
            # Print first 500 chars of content
            print(f"Content preview: {content[:500]}")
