from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
import os


@require_http_methods(["POST"])
def setup_admin_view(request):
    """
    Temporary endpoint to create admin account during initial setup.
    This should be deleted after first use.
    Access: POST /auth/setup-admin/
    """
    try:
        # Only allow this on first setup (no users exist)
        if User.objects.exists():
            return JsonResponse({
                'success': False,
                'message': 'Admin already configured. Delete this endpoint after use.'
            }, status=403)
        
        username = os.getenv('ADMIN_USERNAME', 'admin')
        email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        password = os.getenv('ADMIN_PASSWORD', 'Admin@12345')
        
        # Create superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        # Create profile
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={'citizen_type': 'regular', 'is_verified': True}
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Admin account created successfully',
            'username': username,
            'email': email,
            'note': 'Please login and delete this endpoint from security/views_setup.py and security/urls.py'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)
