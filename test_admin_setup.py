#!/usr/bin/env python
"""
Test the new admin setup page
Run: python test_admin_setup.py
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
print("ADMIN SETUP PAGE TEST")
print("="*60)

with override_settings(ALLOWED_HOSTS=['*']):
    client = Client()
    
    # Check current admin status
    admin_count = User.objects.filter(is_staff=True, is_superuser=True).count()
    print(f"\nCurrent admin accounts: {admin_count}")
    
    # Test setup page access
    print("\n1. Testing setup page accessibility...")
    response = client.get('/admin-panel/setup/')
    print(f"   - Setup page status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✓ Setup page is accessible")
        if response.templates:
            print(f"   - Templates used: {[t.name for t in response.templates]}")
    elif response.status_code in [301, 302, 303, 307, 308]:
        print(f"   - Redirect to: {response.get('Location', 'Unknown')}")
    
    # Test main redirect when no admin exists
    print("\n2. Testing main redirect (should go to setup if no admin)...")
    response = client.get('/')
    print(f"   - Main page status: {response.status_code}")
    location = response.get('Location', 'Unknown')
    print(f"   - Redirects to: {location}")
    
    if '/admin-panel/setup/' in location:
        print(f"   ✓ Correctly redirects to setup page when no admin exists")
    
    # Check form presence
    print("\n3. Checking form fields...")
    response = client.get('/admin-panel/setup/', follow=False)
    content = response.content.decode()
    
    form_fields = [
        ('username', 'Username field'),
        ('email', 'Email field'),
        ('password', 'Password field'),
        ('password_confirm', 'Password confirmation field'),
    ]
    
    for field_name, field_label in form_fields:
        if f'id_{field_name}' in content:
            print(f"   ✓ {field_label} found")
        else:
            print(f"   ❌ {field_label} NOT found")

print("\n" + "="*60)
