#!/usr/bin/env python
"""
Simple admin account creator - works on both local and Render
Just run: python create_admin_simple.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from django.contrib.auth.models import User
from apps.accounts.models import UserProfile

# Admin credentials (from environment or defaults)
username = os.getenv('ADMIN_USERNAME', 'admin')
email = os.getenv('ADMIN_EMAIL', 'admin@example.com') 
password = os.getenv('ADMIN_PASSWORD', 'Admin@12345')

try:
    # Delete existing admin if exists
    User.objects.filter(username=username).delete()
    
    # Create new superuser
    user = User.objects.create_superuser(username, email, password)
    
    # Create profile
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={'citizen_type': 'regular', 'is_verified': True}
    )
    
    print("\n✓ SUCCESS! Admin account created:\n")
    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print(f"  Password: {password}\n")
    print("Go to /auth/login/ and login with these credentials!\n")

except Exception as e:
    print(f"\n✗ ERROR: {str(e)}\n")
    sys.exit(1)
