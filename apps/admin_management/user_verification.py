"""
User Verification Utilities
Functions to handle user account verification and status management
"""

from django.utils import timezone
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
from apps.admin_management.models import VerificationRequest, AdminLog


def verify_user_account(user_id, admin_user, reason=""):
    """
    Verify a user account
    
    Args:
        user_id: User ID to verify
        admin_user: Admin user verifying the account
        reason: Optional reason for verification
        
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'user': User object or None
        }
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Mark user as active
        user.is_active = True
        user.save()
        
        # Update profile if exists
        if hasattr(user, 'profile'):
            user.profile.is_verified = True
            user.profile.verification_date = timezone.now()
            user.profile.save()
        
        # Log the action
        AdminLog.objects.create(
            admin=admin_user,
            action='User Verification',
            description=f"Verified user account: {user.get_full_name()} ({user.email}) - {reason}"
        )
        
        return {
            'success': True,
            'message': f'User account {user.get_full_name()} has been verified and activated',
            'user': user
        }
    except User.DoesNotExist:
        return {
            'success': False,
            'message': f'User with ID {user_id} not found'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error verifying user: {str(e)}'
        }


def unverify_user_account(user_id, admin_user, reason=""):
    """
    Unverify/Deactivate a user account
    
    Args:
        user_id: User ID to unverify
        admin_user: Admin user unverifying the account
        reason: Reason for deactivation
        
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'user': User object or None
        }
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Prevent deactivating the current admin
        if user == admin_user:
            return {
                'success': False,
                'message': 'Cannot deactivate your own account'
            }
        
        # Mark user as inactive
        user.is_active = False
        user.save()
        
        # Update profile if exists
        if hasattr(user, 'profile'):
            user.profile.is_verified = False
            user.profile.save()
        
        # Log the action
        AdminLog.objects.create(
            admin=admin_user,
            action='User Deactivation',
            description=f"Deactivated user account: {user.get_full_name()} ({user.email}) - {reason}"
        )
        
        return {
            'success': True,
            'message': f'User account {user.get_full_name()} has been deactivated',
            'user': user
        }
    except User.DoesNotExist:
        return {
            'success': False,
            'message': f'User with ID {user_id} not found'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error deactivating user: {str(e)}'
        }


def get_user_verification_status(user_id):
    """
    Get detailed verification status for a user
    
    Args:
        user_id: User ID
        
    Returns:
        dict: {
            'is_verified': bool,
            'is_active': bool,
            'email_verified': bool,
            'profile_verified': bool,
            'status': str,
            'message': str
        }
    """
    try:
        user = User.objects.get(id=user_id)
        
        profile_verified = False
        if hasattr(user, 'profile'):
            profile_verified = user.profile.is_verified
        
        status = 'Active & Verified' if (user.is_active and profile_verified) else \
                 'Active & Unverified' if user.is_active else \
                 'Inactive'
        
        return {
            'is_verified': profile_verified,
            'is_active': user.is_active,
            'email_verified': bool(user.email),
            'profile_verified': profile_verified,
            'status': status,
            'message': f'User verification status: {status}',
            'user': user
        }
    except User.DoesNotExist:
        return {
            'is_verified': False,
            'status': 'user_not_found',
            'message': f'User with ID {user_id} not found'
        }
    except Exception as e:
        return {
            'is_verified': False,
            'status': 'error',
            'message': f'Error getting user verification status: {str(e)}'
        }


def get_all_unverified_users():
    """
    Get all unverified users
    
    Returns:
        dict: {
            'total_unverified': int,
            'users': QuerySet,
            'message': str
        }
    """
    try:
        unverified = UserProfile.objects.filter(is_verified=False).select_related('user')
        
        return {
            'total_unverified': unverified.count(),
            'users': unverified,
            'message': f'Found {unverified.count()} unverified users'
        }
    except Exception as e:
        return {
            'total_unverified': 0,
            'users': [],
            'message': f'Error retrieving unverified users: {str(e)}'
        }


def get_all_verified_users():
    """
    Get all verified users
    
    Returns:
        dict: {
            'total_verified': int,
            'users': QuerySet,
            'message': str
        }
    """
    try:
        verified = UserProfile.objects.filter(is_verified=True).select_related('user')
        
        return {
            'total_verified': verified.count(),
            'users': verified,
            'message': f'Found {verified.count()} verified users'
        }
    except Exception as e:
        return {
            'total_verified': 0,
            'users': [],
            'message': f'Error retrieving verified users: {str(e)}'
        }


def get_all_inactive_users():
    """
    Get all inactive users
    
    Returns:
        dict: {
            'total_inactive': int,
            'users': QuerySet,
            'message': str
        }
    """
    try:
        inactive = User.objects.filter(is_active=False)
        
        return {
            'total_inactive': inactive.count(),
            'users': inactive,
            'message': f'Found {inactive.count()} inactive users'
        }
    except Exception as e:
        return {
            'total_inactive': 0,
            'users': [],
            'message': f'Error retrieving inactive users: {str(e)}'
        }


def get_user_verification_stats():
    """
    Get comprehensive user verification statistics
    
    Returns:
        dict: {
            'total_users': int,
            'verified_users': int,
            'unverified_users': int,
            'active_users': int,
            'inactive_users': int,
            'email_verified_users': int,
            'verification_rate': float
        }
    """
    try:
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        inactive_users = total_users - active_users
        email_verified = User.objects.exclude(email='').count()
        
        verified_users = UserProfile.objects.filter(is_verified=True).count()
        unverified_users = UserProfile.objects.filter(is_verified=False).count()
        
        verification_rate = (verified_users / total_users * 100) if total_users > 0 else 0
        
        return {
            'total_users': total_users,
            'verified_users': verified_users,
            'unverified_users': unverified_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'email_verified_users': email_verified,
            'verification_rate': round(verification_rate, 2)
        }
    except Exception as e:
        return {
            'error': True,
            'message': f'Error getting verification stats: {str(e)}'
        }


def bulk_verify_users(user_ids, admin_user, reason=""):
    """
    Verify multiple users at once
    
    Args:
        user_ids: List of user IDs
        admin_user: Admin user verifying
        reason: Reason for bulk verification
        
    Returns:
        dict: {
            'total_processed': int,
            'verified_count': int,
            'failed_count': int,
            'results': list
        }
    """
    results = []
    verified_count = 0
    
    for user_id in user_ids:
        result = verify_user_account(user_id, admin_user, reason)
        results.append(result)
        if result['success']:
            verified_count += 1
    
    return {
        'total_processed': len(user_ids),
        'verified_count': verified_count,
        'failed_count': len(user_ids) - verified_count,
        'results': results
    }


def search_users_by_verification_status(status='unverified'):
    """
    Search users by verification status
    
    Args:
        status: 'verified', 'unverified', 'active', 'inactive'
        
    Returns:
        dict: {
            'status': str,
            'count': int,
            'users': QuerySet,
            'message': str
        }
    """
    try:
        if status == 'verified':
            users = UserProfile.objects.filter(is_verified=True).select_related('user')
        elif status == 'unverified':
            users = UserProfile.objects.filter(is_verified=False).select_related('user')
        elif status == 'active':
            users = User.objects.filter(is_active=True)
        elif status == 'inactive':
            users = User.objects.filter(is_active=False)
        else:
            return {
                'status': 'invalid',
                'count': 0,
                'users': [],
                'message': f'Invalid status: {status}'
            }
        
        return {
            'status': status,
            'count': users.count(),
            'users': users,
            'message': f'Found {users.count()} {status} users'
        }
    except Exception as e:
        return {
            'status': 'error',
            'count': 0,
            'users': [],
            'message': f'Error searching users: {str(e)}'
        }


def can_verify_user(user_id):
    """
    Check if a user can be verified
    
    Args:
        user_id: User ID
        
    Returns:
        dict: {
            'can_verify': bool,
            'reasons': list,
            'message': str
        }
    """
    try:
        user = User.objects.get(id=user_id)
        
        can_verify = True
        reasons = []
        
        # Check if already active
        if user.is_active:
            reasons.append('User account is already active')
        
        # Check if has email
        if not user.email:
            can_verify = False
            reasons.append('User has no email address')
        
        # Check if has profile
        if not hasattr(user, 'profile'):
            reasons.append('User has no profile')
        else:
            if user.profile.is_verified:
                reasons.append('User profile is already verified')
        
        message = 'User can be verified' if can_verify else ' | '.join(reasons)
        
        return {
            'can_verify': can_verify,
            'reasons': reasons,
            'message': message,
            'user': user
        }
    except User.DoesNotExist:
        return {
            'can_verify': False,
            'reasons': [f'User with ID {user_id} not found'],
            'message': 'User not found'
        }
    except Exception as e:
        return {
            'can_verify': False,
            'reasons': [str(e)],
            'message': f'Error validating user: {str(e)}'
        }


def get_pending_verification_requests():
    """
    Get pending verification requests
    
    Returns:
        dict: {
            'total_pending': int,
            'requests': QuerySet,
            'message': str
        }
    """
    try:
        pending = VerificationRequest.objects.filter(status='pending').order_by('-created_at')
        
        return {
            'total_pending': pending.count(),
            'requests': pending,
            'message': f'Found {pending.count()} pending verification requests'
        }
    except Exception as e:
        return {
            'total_pending': 0,
            'requests': [],
            'message': f'Error retrieving pending requests: {str(e)}'
        }
