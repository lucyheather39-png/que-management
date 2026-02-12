#!/usr/bin/env python
"""
Test all pages in the app for functionality
Run: python test_all_pages.py
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

print("\n" + "="*80)
print("COMPREHENSIVE PAGE FUNCTIONALITY TEST")
print("="*80)

with override_settings(ALLOWED_HOSTS=['*']):
    # Create test users
    admin = User.objects.filter(is_staff=True, is_superuser=True, username='admin').first()
    
    regular_user = User.objects.filter(username='test_regular').first()
    if not regular_user:
        regular_user = User.objects.create_user(
            username='test_regular',
            email='regular@test.com',
            password='TestPass123'
        )
        UserProfile.objects.create(
            user=regular_user,
            citizen_type='regular',
            is_verified=True
        )
    
    # Define all pages to test
    pages = {
        'Public Pages': [
            ('/', 'Root redirect', None),
            ('/home/', 'Home page', None),
            ('/auth/login/', 'Login page', None),
            ('/auth/register/', 'Register page', None),
            ('/walkin-queue/', 'Walk-in queue public', None),
        ],
        'Authenticated User Pages': [
            ('/queue/dashboard/', 'User dashboard', regular_user),
            ('/queue/take/', 'Take queue', regular_user),
            ('/queue/list/', 'Queue list', regular_user),
            ('/auth/profile/', 'User profile', regular_user),
            ('/appointment/book/', 'Book appointment', regular_user),
            ('/appointment/my-appointments/', 'My appointments', regular_user),
        ],
        'Admin Pages': [
            ('/admin-panel/', 'Admin dashboard', admin),
            ('/admin-panel/verifications/pending/', 'Pending verifications', admin),
            ('/admin-panel/appointments/pending/', 'Pending appointments', admin),
            ('/admin-panel/queue/management/', 'Queue management', admin),
            ('/admin-panel/users/', 'Users management', admin),
            ('/admin-panel/logs/', 'Activity logs', admin),
            ('/admin-panel/admin/create/', 'Create admin', admin),
            ('/admin-panel/walkin-queues/', 'Walk-in queues', admin),
        ],
    }
    
    results = {}
    
    for category, page_list in pages.items():
        print(f"\n{'='*80}")
        print(f"{category}")
        print(f"{'='*80}")
        
        results[category] = []
        
        for url, name, user in page_list:
            client = Client()
            
            if user:
                # Login if user provided
                if user.username == 'admin':
                    client.login(username='admin', password='Admin@12345')
                else:
                    client.login(username=user.username, password='TestPass123')
            
            try:
                response = client.get(url, follow=True)
                status = response.status_code
                
                # Check status
                if status == 200:
                    print(f"✓ {name:30} {url:35} [200 OK]")
                    results[category].append((name, url, 'OK', status))
                elif status in [301, 302, 303, 307, 308]:
                    final_url = response.redirect_chain[-1][1] if response.redirect_chain else 'Unknown'
                    print(f"→ {name:30} {url:35} [Redirect → {final_url}]")
                    results[category].append((name, url, 'REDIRECT', status))
                else:
                    print(f"❌ {name:30} {url:35} [{status}]")
                    results[category].append((name, url, 'ERROR', status))
                    
            except Exception as e:
                print(f"❌ {name:30} {url:35} [EXCEPTION: {str(e)[:30]}]")
                results[category].append((name, url, 'EXCEPTION', str(e)))
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")
    
    total = 0
    working = 0
    errors = 0
    
    for category, result_list in results.items():
        category_ok = sum(1 for _, _, status, _ in result_list if status == 'OK')
        category_total = len(result_list)
        total += category_total
        working += category_ok
        
        print(f"{category:30} {category_ok:3}/{category_total:3} working")
        
        # Show errors
        for name, url, status, code in result_list:
            if status != 'OK' and status != 'REDIRECT':
                errors += 1
                print(f"  - {name:28} {url:35} [{code}]")
    
    print(f"\n{'='*80}")
    print(f"Total: {working}/{total} pages working ({100*working//total}%)")
    if errors > 0:
        print(f"Issues found: {errors} pages with errors")
    print(f"{'='*80}\n")

