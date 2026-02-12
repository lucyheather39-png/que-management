#!/usr/bin/env python
"""
Test admin login flow
Run: python test_admin_login.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

print("\n" + "="*60)
print("ADMIN LOGIN TEST")
print("="*60)

# Test authenticate function
print("\n1. Testing authentication with admin credentials...")
user = authenticate(username='admin', password='Admin@12345')

if user is not None:
    print(f"   ✓ Authentication successful!")
    print(f"   - Username: {user.username}")
    print(f"   - is_staff: {user.is_staff}")
    print(f"   - is_superuser: {user.is_superuser}")
    print(f"   - is_active: {user.is_active}")
else:
    print(f"   ❌ Authentication FAILED!")
    print(f"   - Check username and password")

# Check decorator test function
print("\n2. Testing is_admin decorator function...")
def is_admin(user):
    return user.is_staff and user.is_superuser

admin = User.objects.get(username='admin')
test_result = is_admin(admin)
print(f"   - is_admin(admin) returns: {test_result}")
if test_result:
    print(f"   ✓ Admin user passes the is_admin test")
else:
    print(f"   ❌ Admin user FAILS the is_admin test")

# Check redirect logic
print("\n3. Testing redirect logic from login_view...")
if admin.is_authenticated:
    if admin.is_staff and admin.is_superuser:
        print(f"   ✓ Admin should be redirected to /admin-panel/")
    else:
        print(f"   ❌ Admin would be redirected to /queue/dashboard/")

print("\n" + "="*60)
