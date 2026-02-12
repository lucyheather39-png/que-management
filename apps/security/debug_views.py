from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required(login_url='security:login')
def debug_user_info(request):
    """
    Debug endpoint to check current user authentication status
    Access: /auth/debug-user/
    """
    user = request.user
    return JsonResponse({
        'authenticated': user.is_authenticated,
        'username': user.username if user.is_authenticated else None,
        'is_staff': user.is_staff if user.is_authenticated else False,
        'is_superuser': user.is_superuser if user.is_authenticated else False,
        'is_active': user.is_active if user.is_authenticated else False,
        'groups': list(user.groups.values_list('name', flat=True)) if user.is_authenticated else [],
        'can_access_admin': (user.is_staff and user.is_superuser) if user.is_authenticated else False,
        'message': 'User is allowed to access admin panel' if (user.is_staff and user.is_superuser) else 'User does not have admin privileges'
    })
