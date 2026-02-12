from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from functools import wraps
from apps.accounts.models import UserProfile
from apps.appointments.models import Appointment
from apps.queues.models import Queue, Service
from .models import VerificationRequest, AdminLog
from .forms import VerificationApprovalForm, AdminCreationForm
from .status_utils import (
    verify_user_verification_status,
    verify_queue_status,
    verify_queue_status_value,
    verify_appointment_status,
    verify_all_user_statuses
)
from .profile_verification import (
    approve_user_profile,
    reject_user_profile,
    get_profile_verification_status,
    get_pending_verifications,
    get_verification_stats,
    can_approve_profile,
    approve_all_pending_verifications,
    approve_pending_verification_by_id
)
from .user_verification import (
    verify_user_account,
    unverify_user_account,
    get_user_verification_status,
    get_all_unverified_users,
    get_all_verified_users,
    get_all_inactive_users,
    get_user_verification_stats,
    bulk_verify_users,
    can_verify_user,
    get_pending_verification_requests
)

def is_admin(user):
    return user.is_staff and user.is_superuser

def setup_first_admin(request):
    """
    Public view to create the first admin account.
    Only accessible if no admin accounts exist yet.
    """
    # Check if any admin exists
    admin_exists = User.objects.filter(is_staff=True, is_superuser=True).exists()
    
    if admin_exists:
        messages.warning(request, 'Admin account already exists. Please login instead.')
        return redirect('security:login')
    
    if request.method == 'POST':
        form = AdminCreationForm(request.POST)
        if form.is_valid():
            try:
                admin_user = form.save()
                
                # Create a UserProfile for the admin
                from apps.accounts.models import UserProfile
                UserProfile.objects.get_or_create(
                    user=admin_user,
                    defaults={
                        'citizen_type': 'regular',
                        'is_verified': True
                    }
                )
                
                messages.success(request, f'Admin account "{admin_user.username}" created successfully! You can now login.')
                return redirect('security:login')
            except Exception as e:
                messages.error(request, f'Error creating admin account: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = AdminCreationForm()
    
    context = {
        'form': form,
        'is_setup': True,
        'title': 'Initial Setup - Create Admin Account',
    }
    return render(request, 'pages/admin/setup_admin.html', context)

def admin_required(view_func):
    """
    Decorator to ensure user is authenticated and is an admin.
    Properly redirects non-admin authenticated users with an error message.
    Also prevents browser caching of admin pages to ensure fresh content.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            if not request.user.is_authenticated:
                messages.error(request, 'You must be logged in to access this page.')
                return redirect('security:login')
            
            if not is_admin(request.user):
                messages.error(request, 'You do not have permission to access the admin dashboard. Only administrators can access this area.')
                return redirect('/queue/dashboard/')
            
            # Call the view function
            response = view_func(request, *args, **kwargs)
            
            # Prevent browser caching of admin pages
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            return response
        
        except Exception as e:
            logger.exception(f'Admin decorator error for user {request.user.id}: {str(e)}')
            messages.error(request, 'An unexpected error occurred. Please try again.')
            return redirect('security:login')
    
    return wrapper

@admin_required
def admin_dashboard_view(request):
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        from django.db.models import Q
        
        # Count all unverified users (both with and without VerificationRequest records)
        pending_verifications = User.objects.filter(profile__is_verified=False).count()
        pending_appointments = Appointment.objects.filter(status='pending').count()
        total_users = User.objects.filter(profile__isnull=False).count()
        
        # Count active online queues only (exclude walk-in queues)
        today_queues = Queue.objects.filter(
            Q(status__in=['waiting', 'serving']) & ~Q(queue_number__startswith='W-')
        ).count()
        
        # Count active walk-in queues
        active_walkin_queues = Queue.objects.filter(
            queue_number__startswith='W-',
            status__in=['waiting', 'serving']
        ).count()
        
        context = {
            'pending_verifications': pending_verifications,
            'pending_appointments': pending_appointments,
            'total_users': total_users,
            'today_queues': today_queues,
            'active_walkin_queues': active_walkin_queues,
        }
        return render(request, 'pages/admin/dashboard.html', context)
    
    except Exception as e:
        logger.exception(f'Admin dashboard view error for user {request.user.id}: {str(e)}')
        messages.error(request, 'Error loading admin dashboard. Please try again or contact support.')
        return render(request, 'pages/admin/dashboard.html', {
            'pending_verifications': 0,
            'pending_appointments': 0,
            'total_users': 0,
            'today_queues': 0,
            'active_walkin_queues': 0,
            'error': True,
        })

@admin_required
def pending_verifications_view(request):
    # Get all unverified users (not just VerificationRequest records)
    unverified_users = User.objects.filter(
        profile__is_verified=False
    ).select_related('profile').order_by('-profile__updated_at')
    
    # Also get explicit pending VerificationRequest records
    pending_requests = VerificationRequest.objects.filter(status='pending').select_related('user', 'user__profile').order_by('-created_at')
    
    # Combine and deduplicate - prefer VerificationRequest data
    verification_ids = set(pending_requests.values_list('user_id', flat=True))
    
    context = {
        'verifications': pending_requests,
        'unverified_users': unverified_users,
        'verification_ids': verification_ids,
    }
    return render(request, 'pages/admin/pending_verifications.html', context)


@admin_required
def approve_all_pending_verifications_view(request):
    """Approve all pending verifications at once"""
    if request.method == 'POST':
        result = approve_all_pending_verifications(request.user, "Auto-approved by admin")
        if result['total_approved'] > 0:
            messages.success(request, result['message'])
        else:
            messages.info(request, result['message'])
        return redirect('admin_management:pending_verifications')
    
    pending_count = VerificationRequest.objects.filter(status='pending').count()
    context = {
        'pending_count': pending_count,
    }
    return render(request, 'pages/admin/approve_all_verifications.html', context)


@admin_required
def approve_single_verification_view(request, verification_id):
    """Quick approve a single verification"""
    if request.method == 'POST':
        result = approve_pending_verification_by_id(verification_id, request.user, "Approved by admin")
        if result['success']:
            messages.success(request, result['message'])
        else:
            messages.error(request, result['message'])
        return redirect('admin_management:pending_verifications')
    
    return redirect('admin_management:pending_verifications')

@admin_required
def approve_verification_view(request, verification_id):
    verification = get_object_or_404(VerificationRequest, id=verification_id)
    
    if request.method == 'POST':
        form = VerificationApprovalForm(request.POST, instance=verification)
        if form.is_valid():
            verification = form.save(commit=False)
            verification.reviewed_by = request.user
            verification.reviewed_at = timezone.now()
            verification.save()
            
            # If approved, use the new profile verification function
            if verification.status == 'approved':
                result = approve_user_profile(verification.user.id, request.user, verification.comments)
                messages.success(request, result['message'])
            else:
                result = reject_user_profile(verification.user.id, request.user, verification.comments)
                messages.info(request, result['message'])
            
            return redirect('admin_management:pending_verifications')
    else:
        form = VerificationApprovalForm(instance=verification)
    
    context = {
        'verification': verification,
        'form': form,
    }
    return render(request, 'pages/admin/approve_verification.html', context)

@admin_required
def pending_appointments_view(request):
    appointments = Appointment.objects.filter(status='pending').order_by('-created_at')
    
    context = {
        'appointments': appointments,
    }
    return render(request, 'pages/admin/pending_appointments.html', context)

@admin_required
def manage_appointment_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['approved', 'rejected']:
            appointment.status = status
            appointment.approved_by = request.user
            appointment.save()
            
            AdminLog.objects.create(
                admin=request.user,
                action='Appointment Management',
                description=f"Appointment {status.capitalize()} for {appointment.user.get_full_name()}"
            )
            
            messages.success(request, f'Appointment {status} successfully!')
            return redirect('admin_management:pending_appointments')
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'pages/admin/manage_appointment.html', context)

@admin_required
def queue_management_view(request):
    from django.db.models import Q
    today_queues = Queue.objects.filter(
        Q(status__in=['waiting', 'serving']) & ~Q(queue_number__startswith='W-')
    ).order_by('priority_level', 'created_at')
    
    context = {
        'queues': today_queues,
    }
    return render(request, 'pages/admin/queue_management.html', context)

@admin_required
def update_queue_status_view(request, queue_id):
    queue_verification = verify_queue_status(queue_id)
    
    if not queue_verification['is_valid']:
        messages.error(request, queue_verification['message'])
        return redirect('admin_management:queue_management')
    
    queue = queue_verification['queue_obj']
    
    if request.method == 'POST':
        status = request.POST.get('status')
        status_verification = verify_queue_status_value(status)
        
        if not status_verification['is_valid']:
            messages.error(request, f"Invalid status. Valid options: {', '.join(status_verification['valid_statuses'])}")
        elif status == 'completed':
            queue_number = queue.queue_number
            queue.delete()
            messages.success(request, f'Queue {queue_number} completed and deleted!')
        else:
            queue.status = status
            if status == 'serving':
                queue.served_at = timezone.now()
            queue.save()
            messages.success(request, f'Queue status updated to {status}!')
    
    return redirect('admin_management:queue_management')

@admin_required
def delete_queue_view(request, queue_id):
    queue = get_object_or_404(Queue, id=queue_id)
    
    if request.method == 'POST':
        queue_number = queue.queue_number
        queue.delete()
        messages.success(request, f'Queue {queue_number} has been deleted!')
    
    return redirect('admin_management:queue_management')

@admin_required
def users_management_view(request):
    users = UserProfile.objects.all().order_by('-created_at')
    
    context = {
        'users': users,
    }
    return render(request, 'pages/admin/users_management.html', context)

@admin_required
def check_account_status_view(request, user_profile_id):
    """Check and display account/verification status for a user"""
    user_profile = get_object_or_404(UserProfile, id=user_profile_id)
    user = user_profile.user
    
    # Get verification status
    verification_result = verify_user_verification_status(user)
    
    # Get all user statuses
    user_statuses = verify_all_user_statuses(user.id)
    
    context = {
        'user_profile': user_profile,
        'user': user,
        'verification': verification_result,
        'user_statuses': user_statuses,
    }
    return render(request, 'pages/admin/check_account_status.html', context)


@admin_required
def verify_user_profile_view(request, user_profile_id):
    """Verify a user profile"""
    user_profile = get_object_or_404(UserProfile, id=user_profile_id)
    user = user_profile.user
    
    if request.method == 'POST':
        result = approve_user_profile(user.id, request.user, "Verified by admin")
        if result['success']:
            messages.success(request, result['message'])
        else:
            messages.error(request, result['message'])
    
    return redirect('admin_management:check_account_status', user_profile_id=user_profile_id)


@admin_required
def unverify_user_profile_view(request, user_profile_id):
    """Unverify a user profile"""
    user_profile = get_object_or_404(UserProfile, id=user_profile_id)
    user = user_profile.user
    
    if request.method == 'POST':
        result = reject_user_profile(user.id, request.user, "Unverified by admin")
        if result['success']:
            messages.success(request, result['message'])
        else:
            messages.error(request, result['message'])
    
    return redirect('admin_management:check_account_status', user_profile_id=user_profile_id)
    
    context = {
        'user_profile': user_profile,
        'user': user,
        'verification': verification_result,
        'user_statuses': user_statuses,
    }
    return render(request, 'pages/admin/check_account_status.html', context)


@admin_required
def admin_logs_view(request):
    logs = AdminLog.objects.all().order_by('-timestamp')[:100]
    
    context = {
        'logs': logs,
    }
    return render(request, 'pages/admin/logs.html', context)

@admin_required
def delete_log_view(request, log_id):
    log = get_object_or_404(AdminLog, id=log_id)
    
    if request.method == 'POST':
        log.delete()
        messages.success(request, 'Log entry deleted successfully!')
    
    return redirect('admin_management:logs')

@admin_required
def create_admin_view(request):
    admins = User.objects.filter(is_staff=True, is_superuser=True).order_by('-date_joined')
    
    if request.method == 'POST':
        form = AdminCreationForm(request.POST)
        if form.is_valid():
            admin_user = form.save()
            
            # Log the action
            AdminLog.objects.create(
                admin=request.user,
                action='Admin Creation',
                description=f"Created new admin account: {admin_user.get_full_name() or admin_user.username}"
            )
            
            messages.success(request, f'Admin account "{admin_user.username}" created successfully!')
            return redirect('admin_management:create_admin')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = AdminCreationForm()
    
    context = {
        'form': form,
        'admins': admins,
    }
    return render(request, 'pages/admin/create_admin.html', context)

@admin_required
def delete_admin_view(request, admin_id):
    admin_user = get_object_or_404(User, id=admin_id, is_staff=True, is_superuser=True)
    
    # Prevent deleting the current user
    if admin_user == request.user:
        messages.error(request, 'You cannot delete your own admin account.')
        return redirect('admin_management:create_admin')
    
    if request.method == 'POST':
        admin_username = admin_user.get_full_name() or admin_user.username
        admin_user.is_staff = False
        admin_user.is_superuser = False
        admin_user.save()
        
        # Log the action
        AdminLog.objects.create(
            admin=request.user,
            action='Admin Removal',
            description=f"Removed admin privileges from: {admin_username}"
        )
        
        messages.success(request, f'Admin privileges removed from "{admin_username}".')
        return redirect('admin_management:create_admin')
    
    context = {
        'admin_user': admin_user,
    }
    return render(request, 'pages/admin/delete_admin_confirm.html', context)

# Status Verification Views

@admin_required
def verify_user_status_view(request, user_id):
    """View to verify user's verification status"""
    user = get_object_or_404(User, id=user_id)
    verification_result = verify_user_verification_status(user)
    
    context = {
        'user': user,
        'verification': verification_result,
    }
    return render(request, 'pages/admin/verify_user_status.html', context)


@admin_required
def verify_all_user_statuses_view(request, user_id):
    """View to verify all statuses for a user"""
    from .status_utils import verify_all_user_statuses
    
    user_statuses = verify_all_user_statuses(user_id)
    
    if 'is_valid' in user_statuses and not user_statuses['is_valid']:
        messages.error(request, user_statuses['message'])
        return redirect('admin_management:users_management')
    
    context = {
        'user_statuses': user_statuses,
    }
    return render(request, 'pages/admin/verify_all_user_statuses.html', context)


# Profile Verification Views

@admin_required
def profile_verification_stats_view(request):
    """View profile verification statistics"""
    stats = get_verification_stats()
    pending_data = get_pending_verifications()
    
    context = {
        'stats': stats,
        'pending_count': pending_data['total_pending'],
    }
    return render(request, 'pages/admin/verification_stats.html', context)


@admin_required
def quick_approve_profile_view(request, user_profile_id):
    """Quick approve user profile"""
    user_profile = get_object_or_404(UserProfile, id=user_profile_id)
    user = user_profile.user
    
    # Check if can approve
    check = can_approve_profile(user.id)
    
    if request.method == 'POST':
        comments = request.POST.get('comments', '')
        result = approve_user_profile(user.id, request.user, comments)
        
        if result['success']:
            messages.success(request, result['message'])
        else:
            messages.error(request, result['message'])
        
        return redirect('admin_management:users_management')
    
    context = {
        'user_profile': user_profile,
        'user': user,
        'can_approve': check['can_approve'],
        'check_result': check,
    }
    return render(request, 'pages/admin/quick_approve_profile.html', context)


@admin_required
def quick_reject_profile_view(request, user_profile_id):
    """Quick reject user profile"""
    user_profile = get_object_or_404(UserProfile, id=user_profile_id)
    user = user_profile.user
    
    if request.method == 'POST':
        comments = request.POST.get('comments', '')
        result = reject_user_profile(user.id, request.user, comments)
        
        if result['success']:
            messages.success(request, result['message'])
        else:
            messages.error(request, result['message'])
        
        return redirect('admin_management:users_management')
    
    context = {
        'user_profile': user_profile,
        'user': user,
    }
    return render(request, 'pages/admin/quick_reject_profile.html', context)


@admin_required
def get_profile_verification_status_view(request, user_profile_id):
    """View profile verification status details"""
    user_profile = get_object_or_404(UserProfile, id=user_profile_id)
    user = user_profile.user
    
    status = get_profile_verification_status(user.id)
    
    context = {
        'user_profile': user_profile,
        'user': user,
        'status': status,
    }
    return render(request, 'pages/admin/profile_verification_status.html', context)

# User Verification Views

@admin_required
def user_verification_stats_view(request):
    """View user verification statistics"""
    stats = get_user_verification_stats()
    pending_data = get_pending_verification_requests()
    
    context = {
        'stats': stats,
        'pending_count': pending_data['total_pending'],
    }
    return render(request, 'pages/admin/user_verification_stats.html', context)


@admin_required
def unverified_users_view(request):
    """View all unverified users"""
    data = get_all_unverified_users()
    
    context = {
        'users': data['users'],
        'total_unverified': data['total_unverified'],
    }
    return render(request, 'pages/admin/unverified_users.html', context)


@admin_required
def verified_users_view(request):
    """View all verified users"""
    data = get_all_verified_users()
    
    context = {
        'users': data['users'],
        'total_verified': data['total_verified'],
    }
    return render(request, 'pages/admin/verified_users.html', context)


@admin_required
def inactive_users_view(request):
    """View all inactive users"""
    data = get_all_inactive_users()
    
    context = {
        'users': data['users'],
        'total_inactive': data['total_inactive'],
    }
    return render(request, 'pages/admin/inactive_users.html', context)


@admin_required
def verify_user_account_view(request, user_id):
    """Verify a user account"""
    user = get_object_or_404(User, id=user_id)
    
    check = can_verify_user(user.id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        result = verify_user_account(user.id, request.user, reason)
        
        if result['success']:
            messages.success(request, result['message'])
        else:
            messages.error(request, result['message'])
        
        return redirect('admin_management:users_management')
    
    context = {
        'user': user,
        'can_verify': check['can_verify'],
        'check_result': check,
    }
    return render(request, 'pages/admin/verify_user_account.html', context)


@admin_required
def deactivate_user_account_view(request, user_id):
    """Deactivate/Unverify a user account"""
    user = get_object_or_404(User, id=user_id)
    
    # Prevent deactivating yourself
    if user == request.user:
        messages.error(request, 'You cannot deactivate your own account')
        return redirect('admin_management:users_management')
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        result = unverify_user_account(user.id, request.user, reason)
        
        if result['success']:
            messages.success(request, result['message'])
        else:
            messages.error(request, result['message'])
        
        return redirect('admin_management:users_management')
    
    context = {
        'user': user,
    }
    return render(request, 'pages/admin/deactivate_user_account.html', context)


@admin_required
def user_verification_status_view(request, user_id):
    """View detailed user verification status"""
    user = get_object_or_404(User, id=user_id)
    
    status = get_user_verification_status(user.id)
    
    context = {
        'user': user,
        'status': status,
    }
    return render(request, 'pages/admin/user_verification_status.html', context)


@admin_required
def walkin_queues_view(request):
    """Admin view for managing walk-in queues"""
    walkin_queues = Queue.objects.filter(
        queue_number__startswith='W-'
    ).select_related('user', 'service').order_by('created_at')
    
    context = {
        'queues': walkin_queues,
    }
    return render(request, 'pages/admin/walkin_queues.html', context)


def public_walkin_queue_view(request):
    """Public page for taking walk-in queue numbers"""
    if request.method == 'POST':
        # Get service ID from POST data
        service_id = request.POST.get('service_id') or request.GET.get('service_id')
        
        if not service_id:
            return JsonResponse({
                'success': False,
                'error': 'Please select a service'
            })
        
        try:
            service = Service.objects.get(id=service_id, is_active=True)
        except Service.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Selected service is not available'
            })
        
        # Generate new walk-in queue number - find the highest existing number
        from django.db.models import Max
        from django.db.models.functions import Cast
        from django.db import models as dj_models
        
        # Get all walk-in queue numbers and find the max
        existing_queues = Queue.objects.filter(
            queue_number__startswith='W-'
        ).values_list('queue_number', flat=True)
        
        max_number = 0
        for queue_num in existing_queues:
            try:
                # Extract number from W-XXX format
                num = int(queue_num.split('-')[1])
                if num > max_number:
                    max_number = num
            except (IndexError, ValueError):
                continue
        
        # Generate next queue number
        next_number = max_number + 1
        queue_number = f"W-{next_number:03d}"
        
        # Get or create a system user for walk-in queues
        system_user, _ = User.objects.get_or_create(
            username='walkin_system',
            defaults={
                'first_name': 'Walk-In',
                'last_name': 'System',
                'email': 'walkin@system.local'
            }
        )
        
        # Create the queue entry
        try:
            queue = Queue.objects.create(
                user=system_user,
                service=service,
                queue_number=queue_number,
                priority_level=3,  # Regular priority
                status='waiting',
                date=timezone.now().date()
            )
            
            # Return JSON response for AJAX
            return JsonResponse({
                'success': True,
                'queue_number': queue_number,
                'created_at': queue.created_at.strftime('%b %d, %Y'),
                'created_time': queue.created_at.strftime('%H:%M'),
                'service': queue.service.name,
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    # GET request - return the page with existing walk-in queues and services
    walkin_queues = Queue.objects.filter(
        queue_number__startswith='W-'
    ).select_related('service').order_by('created_at')[:20]  # Show first 20
    
    services = Service.objects.filter(is_active=True).order_by('name')
    
    context = {
        'queues': walkin_queues,
        'services': services,
    }
    return render(request, 'pages/walkin_queue_public.html', context)


@require_http_methods(["GET"])
def get_walkin_queues_api(request):
    """API endpoint to get recent walk-in queues as JSON"""
    walkin_queues = Queue.objects.filter(
        queue_number__startswith='W-'
    ).select_related('service').order_by('created_at')[:20]
    
    queues_data = []
    for queue in walkin_queues:
        queues_data.append({
            'id': queue.id,
            'queue_number': queue.queue_number,
            'service': queue.service.name,
            'created_at': queue.created_at.strftime('%b %d, %Y'),
            'created_time': queue.created_at.strftime('%H:%M'),
            'status': queue.status,
        })
    
    return JsonResponse({
        'success': True,
        'queues': queues_data,
    })


@require_http_methods(["POST"])
@admin_required
def reset_walkin_queues_view(request):
    """Reset walk-in queue numbers back to W-001 (Admin only)"""
    try:
        # Delete all walk-in queues
        deleted_count, _ = Queue.objects.filter(queue_number__startswith='W-').delete()
        
        AdminLog.objects.create(
            admin=request.user,
            action='Walk-In Queue Management',
            description=f"Reset walk-in queues. Deleted {deleted_count} queue entries."
        )
        
        messages.success(request, f'Walk-in queue numbers reset successfully. Deleted {deleted_count} entries.')
        return JsonResponse({'success': True})
    except Exception as e:
        messages.error(request, f'Error resetting queues: {str(e)}')
        return JsonResponse({'success': False, 'error': str(e)})