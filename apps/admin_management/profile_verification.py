"""
Profile Verification Utilities
Functions to handle user profile verification
"""

from django.utils import timezone
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
from apps.admin_management.models import VerificationRequest, AdminLog


def approve_user_profile(user_id, admin_user, comments=""):
    """
    Approve a user's profile verification
    
    Args:
        user_id: User ID to verify
        admin_user: Admin user approving the verification
        comments: Optional comments about approval
        
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'user': User object or None,
            'profile': UserProfile object or None
        }
    """
    try:
        user = User.objects.get(id=user_id)
        profile = user.profile
        
        # Update profile verification
        profile.is_verified = True
        profile.verification_date = timezone.now()
        profile.save()
        
        # Update verification request
        try:
            verification = VerificationRequest.objects.get(user=user)
            verification.status = 'approved'
            verification.reviewed_by = admin_user
            verification.reviewed_at = timezone.now()
            verification.comments = comments
            verification.save()
        except VerificationRequest.DoesNotExist:
            # Create new verification request if doesn't exist
            VerificationRequest.objects.create(
                user=user,
                status='approved',
                reviewed_by=admin_user,
                reviewed_at=timezone.now(),
                comments=comments
            )
        
        # Log the action
        AdminLog.objects.create(
            admin=admin_user,
            action='Profile Approval',
            description=f"Approved profile for user: {user.get_full_name()} ({user.email})"
        )
        
        return {
            'success': True,
            'message': f'Profile for {user.get_full_name()} has been verified',
            'user': user,
            'profile': profile
        }
    except User.DoesNotExist:
        return {
            'success': False,
            'message': f'User with ID {user_id} not found'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error approving profile: {str(e)}'
        }


def reject_user_profile(user_id, admin_user, comments=""):
    """
    Reject a user's profile verification
    
    Args:
        user_id: User ID to reject
        admin_user: Admin user rejecting the verification
        comments: Reason for rejection
        
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'user': User object or None
        }
    """
    try:
        user = User.objects.get(id=user_id)
        profile = user.profile
        
        # Keep profile unverified
        profile.is_verified = False
        profile.save()
        
        # Update verification request
        try:
            verification = VerificationRequest.objects.get(user=user)
            verification.status = 'rejected'
            verification.reviewed_by = admin_user
            verification.reviewed_at = timezone.now()
            verification.comments = comments
            verification.save()
        except VerificationRequest.DoesNotExist:
            # Create new verification request if doesn't exist
            VerificationRequest.objects.create(
                user=user,
                status='rejected',
                reviewed_by=admin_user,
                reviewed_at=timezone.now(),
                comments=comments
            )
        
        # Log the action
        AdminLog.objects.create(
            admin=admin_user,
            action='Profile Rejection',
            description=f"Rejected profile for user: {user.get_full_name()} ({user.email}) - Reason: {comments}"
        )
        
        return {
            'success': True,
            'message': f'Profile for {user.get_full_name()} has been rejected',
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
            'message': f'Error rejecting profile: {str(e)}'
        }


def get_profile_verification_status(user_id):
    """
    Get detailed verification status for a user profile
    
    Args:
        user_id: User ID
        
    Returns:
        dict: {
            'is_verified': bool,
            'status': str ('pending', 'approved', 'rejected'),
            'verification_date': datetime or None,
            'reviewed_by': User or None,
            'reviewed_at': datetime or None,
            'comments': str,
            'message': str
        }
    """
    try:
        user = User.objects.get(id=user_id)
        profile = user.profile
        
        verification_data = {
            'is_verified': profile.is_verified,
            'verification_date': profile.verification_date if hasattr(profile, 'verification_date') else None,
        }
        
        # Get verification request if exists
        try:
            verification = VerificationRequest.objects.get(user=user)
            verification_data.update({
                'status': verification.status,
                'reviewed_by': verification.reviewed_by,
                'reviewed_at': verification.reviewed_at,
                'comments': verification.comments,
                'verification_request_id': verification.id
            })
        except VerificationRequest.DoesNotExist:
            verification_data.update({
                'status': 'no_request',
                'reviewed_by': None,
                'reviewed_at': None,
                'comments': 'No verification request submitted'
            })
        
        status_text = 'Verified' if verification_data['is_verified'] else 'Not Verified'
        verification_data['message'] = f"Profile status: {status_text}"
        
        return verification_data
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
            'message': f'Error getting verification status: {str(e)}'
        }


def get_pending_verifications():
    """
    Get all pending verification requests
    
    Returns:
        dict: {
            'total_pending': int,
            'verifications': QuerySet of VerificationRequest,
            'message': str
        }
    """
    try:
        pending = VerificationRequest.objects.filter(status='pending').order_by('-created_at')
        
        return {
            'total_pending': pending.count(),
            'verifications': pending,
            'message': f'Found {pending.count()} pending verification requests'
        }
    except Exception as e:
        return {
            'total_pending': 0,
            'verifications': [],
            'message': f'Error retrieving pending verifications: {str(e)}'
        }


def get_verification_stats():
    """
    Get verification statistics
    
    Returns:
        dict: {
            'total_users': int,
            'verified_users': int,
            'unverified_users': int,
            'pending_requests': int,
            'approved_requests': int,
            'rejected_requests': int,
            'verification_rate': float (percentage)
        }
    """
    try:
        all_users = UserProfile.objects.count()
        verified_users = UserProfile.objects.filter(is_verified=True).count()
        unverified_users = all_users - verified_users
        
        pending_requests = VerificationRequest.objects.filter(status='pending').count()
        approved_requests = VerificationRequest.objects.filter(status='approved').count()
        rejected_requests = VerificationRequest.objects.filter(status='rejected').count()
        
        verification_rate = (verified_users / all_users * 100) if all_users > 0 else 0
        
        return {
            'total_users': all_users,
            'verified_users': verified_users,
            'unverified_users': unverified_users,
            'pending_requests': pending_requests,
            'approved_requests': approved_requests,
            'rejected_requests': rejected_requests,
            'verification_rate': round(verification_rate, 2)
        }
    except Exception as e:
        return {
            'error': True,
            'message': f'Error getting verification stats: {str(e)}'
        }


def bulk_approve_profiles(user_ids, admin_user, comments=""):
    """
    Approve multiple user profiles at once
    
    Args:
        user_ids: List of user IDs
        admin_user: Admin user approving
        comments: Comments for approval
        
    Returns:
        dict: {
            'total_processed': int,
            'approved_count': int,
            'failed_count': int,
            'results': list of results for each user
        }
    """
    results = []
    approved_count = 0
    
    for user_id in user_ids:
        result = approve_user_profile(user_id, admin_user, comments)
        results.append(result)
        if result['success']:
            approved_count += 1
    
    return {
        'total_processed': len(user_ids),
        'approved_count': approved_count,
        'failed_count': len(user_ids) - approved_count,
        'results': results
    }


def can_approve_profile(user_id):
    """
    Check if a profile can be approved (validation)
    
    Args:
        user_id: User ID
        
    Returns:
        dict: {
            'can_approve': bool,
            'reasons': list of reasons if cannot approve,
            'message': str
        }
    """
    try:
        user = User.objects.get(id=user_id)
        profile = user.profile
        
        can_approve = True
        reasons = []
        
        # Check if already verified
        if profile.is_verified:
            can_approve = False
            reasons.append('Profile is already verified')
        
        # Check if email is verified
        if not user.email:
            can_approve = False
            reasons.append('User has no email address')
        
        # Check if verification request exists
        try:
            verification = VerificationRequest.objects.get(user=user)
            if verification.status == 'approved':
                can_approve = False
                reasons.append('Verification already approved')
            elif verification.status == 'rejected':
                reasons.append('Previous verification was rejected (can still approve)')
        except VerificationRequest.DoesNotExist:
            reasons.append('No verification request found (can still approve)')
        
        message = 'Profile can be approved' if can_approve else ' | '.join(reasons)
        
        return {
            'can_approve': can_approve,
            'reasons': reasons,
            'message': message,
            'user': user,
            'profile': profile
        }
    except User.DoesNotExist:
        return {
            'can_approve': False,
            'reasons': [f'User with ID {user_id} not found'],
            'message': f'User not found'
        }
    except Exception as e:
        return {
            'can_approve': False,
            'reasons': [str(e)],
            'message': f'Error validating profile: {str(e)}'
        }


def approve_all_pending_verifications(admin_user, comments="Auto-approved by admin"):
    """
    Approve all pending verification requests
    
    Args:
        admin_user: Admin user approving
        comments: Comments for approval
        
    Returns:
        dict: {
            'total_approved': int,
            'failed': int,
            'results': list of results,
            'message': str
        }
    """
    try:
        pending_verifications = VerificationRequest.objects.filter(status='pending')
        total = pending_verifications.count()
        results = []
        approved_count = 0
        
        for verification in pending_verifications:
            try:
                user = verification.user
                profile = user.profile
                
                # Update profile
                profile.is_verified = True
                profile.verification_date = timezone.now()
                profile.save()
                
                # Update verification request
                verification.status = 'approved'
                verification.reviewed_by = admin_user
                verification.reviewed_at = timezone.now()
                verification.comments = comments
                verification.save()
                
                # Log the action
                AdminLog.objects.create(
                    admin=admin_user,
                    action='Bulk Profile Approval',
                    description=f"Auto-approved profile for user: {user.get_full_name()} ({user.email})"
                )
                
                results.append({
                    'success': True,
                    'user': user.get_full_name(),
                    'message': f'Approved {user.get_full_name()}'
                })
                approved_count += 1
            except Exception as e:
                results.append({
                    'success': False,
                    'user': verification.user.get_full_name(),
                    'message': f'Error: {str(e)}'
                })
        
        return {
            'total_approved': approved_count,
            'failed': total - approved_count,
            'total_processed': total,
            'results': results,
            'message': f'Successfully approved {approved_count} out of {total} pending verifications'
        }
    except Exception as e:
        return {
            'total_approved': 0,
            'failed': 0,
            'message': f'Error approving pending verifications: {str(e)}'
        }


def approve_pending_verification_by_id(verification_id, admin_user, comments=""):
    """
    Approve a specific pending verification
    
    Args:
        verification_id: Verification request ID
        admin_user: Admin user approving
        comments: Comments for approval
        
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'user': User object or None
        }
    """
    try:
        verification = VerificationRequest.objects.get(id=verification_id, status='pending')
        user = verification.user
        profile = user.profile
        
        # Update profile
        profile.is_verified = True
        profile.verification_date = timezone.now()
        profile.save()
        
        # Update verification request
        verification.status = 'approved'
        verification.reviewed_by = admin_user
        verification.reviewed_at = timezone.now()
        verification.comments = comments
        verification.save()
        
        # Log the action
        AdminLog.objects.create(
            admin=admin_user,
            action='Profile Approval',
            description=f"Approved profile for user: {user.get_full_name()} ({user.email})"
        )
        
        return {
            'success': True,
            'message': f'Profile for {user.get_full_name()} has been verified',
            'user': user
        }
    except VerificationRequest.DoesNotExist:
        return {
            'success': False,
            'message': 'Verification request not found or already processed'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error approving verification: {str(e)}'
        }
