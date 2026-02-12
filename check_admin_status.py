#!/usr/bin/env python
"""
Diagnostic script to check admin account status
Run: python check_admin_status.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from django.contrib.auth.models import User

print("\n" + "="*60)
print("ADMIN ACCOUNT STATUS CHECK")
print("="*60)

admin = User.objects.filter(username='admin').first()

if not admin:
    print("\n❌ NO ADMIN ACCOUNT FOUND")
    print("\nTotal users in database:", User.objects.count())
    print("\nCreating admin account...\n")
    from apps.accounts.models import UserProfile
    admin = User.objects.create_superuser('admin', 'admin@example.com', 'Admin@12345')
    profile, _ = UserProfile.objects.get_or_create(
        user=admin,
        defaults={'citizen_type': 'regular', 'is_verified': True}
    )
    print("✓ Admin account created successfully!")
else:
    print(f"\n✓ Admin account found")
    
print("\nAdmin Account Details:")
print(f"  Username: {admin.username}")
print(f"  Email: {admin.email}")
print(f"  is_staff: {admin.is_staff} {'✓' if admin.is_staff else '❌'}")
print(f"  is_superuser: {admin.is_superuser} {'✓' if admin.is_superuser else '❌'}")
print(f"  is_active: {admin.is_active} {'✓' if admin.is_active else '❌'}")

if admin.profile:
    print(f"  Profile exists: ✓")
    print(f"    - citizen_type: {admin.profile.citizen_type}")
    print(f"    - is_verified: {admin.profile.is_verified}")
else:
    print(f"  Profile exists: ❌ (creating...)")
    from apps.accounts.models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(
        user=admin,
        defaults={'citizen_type': 'regular', 'is_verified': True}
    )
    print(f"    - Created with citizen_type: regular")
    print(f"    - is_verified: True")

if admin.is_staff and admin.is_superuser and admin.is_active:
    print("\n✓ ADMIN ACCOUNT IS FULLY CONFIGURED AND READY TO USE!")
    print("\nLogin Credentials:")
    print(f"  Username: admin")
    print(f"  Password: Admin@12345")
else:
    print("\n⚠ Admin account has missing permissions - fixing...")
    admin.is_staff = True
    admin.is_superuser = True
    admin.is_active = True
    admin.save()
    print("✓ Fixed! Admin now has all necessary permissions.")

print("\n" + "="*60 + "\n")
