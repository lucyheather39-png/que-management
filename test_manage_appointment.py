import os
import django
from django.test import Client
from django.test.utils import override_settings
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
from apps.appointments.models import Appointment

# Create test admin
admin_user, created = User.objects.get_or_create(
    username='test_manage_appt',
    defaults={
        'email': 'testappt@test.com',
        'is_staff': True,
        'is_superuser': True,
    }
)

if created:
    admin_user.set_password('TestAppt@123')
    admin_user.save()
    UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={'citizen_type': 'regular', 'is_verified': True}
    )

# Create a test user for appointment
test_user, _ = User.objects.get_or_create(
    username='appointee',
    defaults={'email': 'appointee@test.com', 'first_name': 'John', 'last_name': 'Doe'}
)
test_user_profile, _ = UserProfile.objects.get_or_create(
    user=test_user,
    defaults={'citizen_type': 'senior_citizen', 'is_verified': True}
)

# Create a test appointment with correct fields
future_date = datetime.now() + timedelta(days=5)
appointment, _ = Appointment.objects.get_or_create(
    user=test_user,
    appointment_date=future_date,
    service_type='Registration',
    defaults={
        'purpose': 'Test appointment',
        'status': 'pending',
        'is_senior_citizen': True
    }
)

print(f"Test appointment ID: {appointment.id}\n")

# Test with override settings for testserver
with override_settings(ALLOWED_HOSTS=['*']):
    client = Client()
    login_success = client.login(username='test_manage_appt', password='TestAppt@123')
    print(f"Login successful: {login_success}\n")
    
    # Test manage appointment page
    url = f'/admin-panel/appointments/{appointment.id}/manage/'
    print(f"Testing: {url}")
    print("=" * 80)
    
    response = client.get(url)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Page loaded successfully")
        content = response.content.decode()
        if 'Manage Appointment' in content or 'John Doe' in content or appointment.service_type in content:
            print("✓ Correct content found")
        else:
            print("⚠ Page loaded but content check inconclusive")
            print(f"First 300 chars: {content[:300]}")
    else:
        print(f"✗ Error status code: {response.status_code}")
        if response.status_code == 404:
            print("Error: Page not found (404)")
        elif response.status_code == 500:
            print("Error: Server error (500)")
            try:
                print(f"Response content: {response.content.decode()[:800]}")
            except:
                print("Could not decode response")
        else:
            try:
                print(f"Response: {response.content.decode()[:500]}")
            except:
                print("Could not decode response")

