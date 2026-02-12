#!/usr/bin/env python
"""
Test admin decorator and authentication
Run: python test_admin_auth.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from django.test import Client, override_settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

print("\n" + "="*60)
print("ADMIN AUTHENTICATION TEST")
print("="*60)

with override_settings(ALLOWED_HOSTS=['*']):
    # Test all admin users
    admins = User.objects.filter(is_staff=True, is_superuser=True)
    
    print(f"\nTotal admin users found: {admins.count()}")
    
    for admin in admins:
        print(f"\n  - User: {admin.username}")
        print(f"    is_staff: {admin.is_staff}")
        print(f"    is_superuser: {admin.is_superuser}")
        print(f"    is_active: {admin.is_active}")
        
        # Try authentication with default password
        auth_result = authenticate(username=admin.username, password='Admin@12345')
        if auth_result:
            print(f"    ✓ Authenticated with 'Admin@12345'")
        else:
            print(f"    ❌ Failed to authenticate with 'Admin@12345'")
    
    # Test with first admin
    if admins.exists():
        print(f"\n\nTesting admin dashboard access with first admin...")
        first_admin = admins.first()
        
        client = Client()
        
        # Try manual login
        print(f"\n1. Testing direct login to get session...")
        response = client.post('/auth/login/', {
            'username': first_admin.username,
            'password': 'Admin@12345'
        }, follow=False)
        
        print(f"   - Login response status: {response.status_code}")
        print(f"   - Redirects to: {response.get('Location', 'No redirect')}")
        
        # Check session
        if '_auth_user_id' in client.session:
            print(f"   ✓ User authenticated in session: {client.session.get('_auth_user_id')}")
        else:
            print(f"   ❌ No user in session")
        
        # Test dashboard with credentials in headers
        print(f"\n2. Testing admin dashboard with authenticated session...")
        response = client.get('/admin-panel/', follow=False)
        print(f"   - Dashboard status: {response.status_code}")
        print(f"   - Redirects to: {response.get('Location', 'No redirect')}")
        
        # Check admin status in decorator
        print(f"\n3. Checking admin status...")
        from apps.admin_management.views import is_admin
        user = User.objects.get(username=first_admin.username)
        print(f"   - is_admin(user) = {is_admin(user)}")
        print(f"   - user.is_staff = {user.is_staff}")
        print(f"   - user.is_superuser = {user.is_superuser}")

print("\n" + "="*60)
