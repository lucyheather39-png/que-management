#!/usr/bin/env python
"""
Test admin panel access using Django test client
Run: python test_admin_access.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from django.test import Client
from django.contrib.auth.models import User

print("\n" + "="*60)
print("ADMIN PANEL ACCESS TEST")
print("="*60)

client = Client()

# Get or create admin user
admin = User.objects.get(username='admin')

print("\n1. Testing login flow...")
response = client.post('/auth/login/', {
    'username': 'admin',
    'password': 'Admin@12345'
})

print(f"   - Login POST status: {response.status_code}")
print(f"   - Login redirect location: {response.get('Location', 'No redirect')}")

# Check if user is authenticated in session
print(f"   - Session authenticated: {client.session.get('_auth_user_id') is not None}")

# Now try to access admin panel
print("\n2. Testing admin panel access...")
response = client.get('/admin-panel/')
print(f"   - Admin panel status: {response.status_code}")
print(f"   - Admin panel redirect location: {response.get('Location', 'No redirect')}")

# Check templates used
if response.templates:
    print(f"   - Templates used: {[t.name for t in response.templates]}")

# Get the actual response content to see the error
if response.status_code != 200:
    print(f"\n   Response redirects to: {response.get('Location', 'No location header')}")

# Try accessing dashboard directly with login
print("\n3. Testing with authenticated session...")
client.login(username='admin', password='Admin@12345')
response = client.get('/admin-panel/')
print(f"   - Status code: {response.status_code}")
if response.status_code == 200:
    print(f"   ✓ Admin can access dashboard after login")
else:
    print(f"   ❌ Admin cannot access dashboard. Redirected to: {response.get('Location', 'Unknown')}")

print("\n" + "="*60)
