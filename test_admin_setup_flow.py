#!/usr/bin/env python
"""
Test admin setup and login flow for redirect issues
Run: python test_admin_setup_flow.py
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
print("ADMIN SETUP AND LOGIN FLOW TEST")
print("="*60)

with override_settings(ALLOWED_HOSTS=['*']):
    # First, backup existing admins
    existing_admins = list(User.objects.filter(is_staff=True, is_superuser=True).values_list('username', flat=True))
    print(f"\nExisting admin accounts: {existing_admins}")
    
    # Test 1: Login page access when admin exists
    print("\n1. Testing login page when admin exists...")
    client = Client()
    response = client.get('/auth/login/', follow=False)
    print(f"   - Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✓ Login page accessible")
    else:
        print(f"   - Redirect to: {response.get('Location', 'Unknown')}")
    
    # Test 2: Root redirect when authenticated
    print("\n2. Testing root redirect for authenticated user...")
    admin_user = User.objects.filter(is_staff=True, is_superuser=True).first()
    if admin_user:
        client2 = Client()
        client2.login(username=admin_user.username, password='Admin@12345')
        response = client2.get('/', follow=False)
        print(f"   - Status: {response.status_code}")
        location = response.get('Location', 'No redirect')
        print(f"   - Redirects to: {location}")
        if '/admin-panel/' in location:
            print(f"   ✓ Admin correctly redirected to admin panel")
    
    # Test 3: Root redirect when unauthenticated
    print("\n3. Testing root redirect for unauthenticated user...")
    client3 = Client()
    response = client3.get('/', follow=False)
    print(f"   - Status: {response.status_code}")
    location = response.get('Location', 'No redirect')
    print(f"   - Redirects to: {location}")
    if '/auth/login/' in location:
        print(f"   ✓ Unauthenticated user redirected to login")
    
    # Test 4: Follow login redirect (check for redirect loop)
    print("\n4. Testing login page with follow redirects (loop detection)...")
    client4 = Client()
    response = client4.get('/auth/login/', follow=True)
    print(f"   - Final status: {response.status_code}")
    print(f"   - Redirect count: {len(response.redirect_chain)}")
    
    if response.redirect_chain:
        print(f"   - Redirect chain:")
        for idx, (rsp, url) in enumerate(response.redirect_chain):
            print(f"     {idx+1}. {rsp.status_code} → {url}")
    
    if response.status_code == 200 and len(response.redirect_chain) < 3:
        print(f"   ✓ No excessive redirects")
    else:
        print(f"   ❌ Excessive redirects detected!")
    
    # Test 5: Direct setup page access
    print("\n5. Testing setup page access when admin exists...")
    client5 = Client()
    response = client5.get('/admin-panel/setup/', follow=False)
    print(f"   - Status: {response.status_code}")
    location = response.get('Location', 'No redirect')
    if response.status_code in [301, 302, 303, 307, 308]:
        print(f"   - Redirects to: {location}")
        if '/auth/login/' in location:
            print(f"   ✓ Correctly redirected to login (admin exists)")
    elif response.status_code == 200:
        print(f"   - Page loaded (setup mode)")

print("\n" + "="*60)
