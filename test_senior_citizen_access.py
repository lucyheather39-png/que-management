#!/usr/bin/env python
"""
Test senior citizen dashboard access for redirect loop
Run: python test_senior_citizen_access.py
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
print("SENIOR CITIZEN DASHBOARD ACCESS TEST")
print("="*60)

with override_settings(ALLOWED_HOSTS=['*']):
    # Create a senior citizen test user
    username = 'senior_test_user'
    user = User.objects.filter(username=username).first()
    
    if not user:
        print("\nCreating senior citizen test user...")
        user = User.objects.create_user(
            username=username,
            email='senior@test.com',
            password='TestPass123'
        )
        profile = UserProfile.objects.create(
            user=user,
            citizen_type='senior',
            is_verified=True,
            contact_number='1234567890'
        )
        print(f"✓ Created user: {username}")
        print(f"  - Citizen Type: {profile.citizen_type}")
        print(f"  - Is Verified: {profile.is_verified}")
    else:
        profile = user.profile
        print(f"\nUsing existing user: {username}")
        print(f"  - Citizen Type: {profile.citizen_type}")
        print(f"  - Is Verified: {profile.is_verified}")
    
    client = Client()
    
    # Test login
    print("\n1. Testing login...")
    response = client.post('/auth/login/', {
        'username': username,
        'password': 'TestPass123'
    }, follow=False)
    
    print(f"   - Login status: {response.status_code}")
    print(f"   - Login redirects to: {response.get('Location', 'No redirect')}")
    
    # Check if authenticated
    if client.session.get('_auth_user_id'):
        print(f"   ✓ User authenticated in session")
    else:
        print(f"   ❌ User NOT authenticated")
    
    # Test dashboard access with redirect loop detection
    print("\n2. Testing dashboard access (follow up to 10 redirects)...")
    response = client.get('/queue/dashboard/', follow=True)
    
    print(f"   - Final status: {response.status_code}")
    print(f"   - Number of redirects: {len(response.redirect_chain)}")
    
    if response.redirect_chain:
        print(f"   - Redirect chain:")
        for redirect_response, redirect_url in response.redirect_chain:
            print(f"     → {redirect_response.status_code} → {redirect_url}")
    
    if response.status_code == 200:
        print(f"   ✓ Dashboard loaded successfully")
        if response.templates:
            print(f"   - Templates: {[t.name for t in response.templates]}")
    else:
        print(f"   ❌ Dashboard returned status {response.status_code}")
    
    # Direct dashboard access
    print("\n3. Testing direct dashboard access (no follow)...")
    client2 = Client()
    client2.login(username=username, password='TestPass123')
    response = client2.get('/queue/dashboard/', follow=False)
    
    print(f"   - Direct status: {response.status_code}")
    if response.status_code in [301, 302, 307, 308]:
        print(f"   - Redirect to: {response.get('Location', 'Unknown')}")
    elif response.status_code == 200:
        print(f"   ✓ Direct access successful")

print("\n" + "="*60)
