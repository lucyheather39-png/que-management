#!/usr/bin/env python
"""
Test admin panel access with proper test client setup
Run: python test_admin_access_fixed.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))

# Override ALLOWED_HOSTS for testing
os.environ['ALLOWED_HOSTS'] = 'localhost,127.0.0.1,testserver,*'

django.setup()

from django.test import Client, override_settings
from django.contrib.auth.models import User

print("\n" + "="*60)
print("ADMIN PANEL ACCESS TEST (FIXED)")
print("="*60)

with override_settings(ALLOWED_HOSTS=['*']):
    client = Client()
    
    # Get or create admin user
    admin = User.objects.get(username='admin')
    
    print("\n1. Testing login and redirect...")
    response = client.post('/auth/login/', {
        'username': 'admin',
        'password': 'Admin@12345'
    }, follow=False)
    
    print(f"   - Login POST status: {response.status_code}")
    print(f"   - Login redirect location: {response.get('Location', 'No redirect')}")
    
    # Try accessing admin panel
    print("\n2. Testing admin panel access (POST auth)...")
    response = client.get('/admin-panel/')
    print(f"   - Admin panel status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✓ Admin can access dashboard after login")
    else:
        print(f"   - Redirected to: {response.get('Location', 'Unknown')}")
    
    # Login and then test
    print("\n3. Testing with authenticated session...")
    client.login(username='admin', password='Admin@12345')
    response = client.get('/admin-panel/')
    print(f"   - Admin panel status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✓ Admin can access dashboard after authenticated login")
        if response.templates:
            print(f"   - Templates used: {[t.name for t in response.templates]}")
    else:
        print(f"   ❌ Admin cannot access dashboard")
        print(f"   - Redirected to: {response.get('Location', 'Unknown')}")
        
    # Test with non-admin user
    print("\n4. Testing with non-admin authenticated user...")
    from django.contrib.auth.models import User
    
    # Create a non-admin user
    non_admin = User.objects.filter(username='testuser').first()
    if not non_admin:
        non_admin = User.objects.create_user('testuser', 'test@example.com', 'TestPass123')
        from apps.accounts.models import UserProfile
        UserProfile.objects.create(user=non_admin, citizen_type='regular', is_verified=False)
    
    client2 = Client()
    client2.login(username='testuser', password='TestPass123')
    response = client2.get('/admin-panel/')
    
    print(f"   - Non-admin admin panel status: {response.status_code}")
    if response.status_code in [301, 302, 303, 307, 308]:
        location = response.get('Location', 'Unknown')
        print(f"   ✓ Non-admin properly redirected to: {location}")
    else:
        print(f"   ❌ Non-admin not redirected properly")

print("\n" + "="*60)
