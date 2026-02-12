"""
Status Verification Utilities
Functions to verify and validate different status types in the system
"""

from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
from apps.queues.models import Queue
from apps.appointments.models import Appointment


def verify_user_verification_status(user):
    """
    Verify if a user's verification is approved
    
    Args:
        user: User object
        
    Returns:
        dict: {
            'is_verified': bool,
            'status': str ('pending', 'approved', 'rejected'),
            'message': str
        }
    """
    try:
        if hasattr(user, 'verification_request'):
            verification = user.verification_request
            return {
                'is_verified': verification.status == 'approved',
                'status': verification.status,
                'message': f"User verification status: {verification.status}",
                'verification_obj': verification
            }
        else:
            return {
                'is_verified': False,
                'status': 'no_request',
                'message': "No verification request found for this user"
            }
    except Exception as e:
        return {
            'is_verified': False,
            'status': 'error',
            'message': f"Error checking user verification: {str(e)}"
        }


def verify_queue_status(queue_id):
    """
    Verify if a queue exists and return its status
    
    Args:
        queue_id: Queue ID
        
    Returns:
        dict: {
            'is_valid': bool,
            'status': str ('waiting', 'serving', 'completed', 'cancelled'),
            'message': str,
            'queue_obj': Queue object or None
        }
    """
    try:
        queue = Queue.objects.get(id=queue_id)
        return {
            'is_valid': True,
            'status': queue.status,
            'message': f"Queue {queue.queue_number} status: {queue.get_status_display()}",
            'queue_obj': queue
        }
    except Queue.DoesNotExist:
        return {
            'is_valid': False,
            'status': 'not_found',
            'message': f"Queue with ID {queue_id} not found"
        }
    except Exception as e:
        return {
            'is_valid': False,
            'status': 'error',
            'message': f"Error verifying queue status: {str(e)}"
        }


def verify_queue_status_value(status):
    """
    Verify if a status value is valid for queues
    
    Args:
        status: Status string
        
    Returns:
        dict: {
            'is_valid': bool,
            'valid_statuses': list,
            'message': str
        }
    """
    valid_statuses = ['waiting', 'serving', 'completed', 'cancelled']
    
    return {
        'is_valid': status in valid_statuses,
        'valid_statuses': valid_statuses,
        'message': f"Status '{status}' is {'valid' if status in valid_statuses else 'invalid'}"
    }


def verify_appointment_status(appointment_id):
    """
    Verify if an appointment exists and return its status
    
    Args:
        appointment_id: Appointment ID
        
    Returns:
        dict: {
            'is_valid': bool,
            'status': str ('pending', 'approved', 'rejected', 'completed', 'cancelled'),
            'message': str,
            'appointment_obj': Appointment object or None
        }
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        return {
            'is_valid': True,
            'status': appointment.status,
            'message': f"Appointment status: {appointment.get_status_display()}",
            'appointment_obj': appointment
        }
    except Appointment.DoesNotExist:
        return {
            'is_valid': False,
            'status': 'not_found',
            'message': f"Appointment with ID {appointment_id} not found"
        }
    except Exception as e:
        return {
            'is_valid': False,
            'status': 'error',
            'message': f"Error verifying appointment status: {str(e)}"
        }


def verify_appointment_status_value(status):
    """
    Verify if a status value is valid for appointments
    
    Args:
        status: Status string
        
    Returns:
        dict: {
            'is_valid': bool,
            'valid_statuses': list,
            'message': str
        }
    """
    valid_statuses = ['pending', 'approved', 'rejected', 'completed', 'cancelled']
    
    return {
        'is_valid': status in valid_statuses,
        'valid_statuses': valid_statuses,
        'message': f"Status '{status}' is {'valid' if status in valid_statuses else 'invalid'}"
    }


def verify_verification_status(status):
    """
    Verify if a status value is valid for verification requests
    
    Args:
        status: Status string
        
    Returns:
        dict: {
            'is_valid': bool,
            'valid_statuses': list,
            'message': str
        }
    """
    valid_statuses = ['pending', 'approved', 'rejected']
    
    return {
        'is_valid': status in valid_statuses,
        'valid_statuses': valid_statuses,
        'message': f"Status '{status}' is {'valid' if status in valid_statuses else 'invalid'}"
    }


def verify_all_user_statuses(user_id):
    """
    Get comprehensive status verification for a user
    
    Args:
        user_id: User ID
        
    Returns:
        dict: Contains all status information for the user
    """
    try:
        user = User.objects.get(id=user_id)
        
        verification = verify_user_verification_status(user)
        
        # Get user queues
        queues = Queue.objects.filter(user=user)
        queue_statuses = {
            'total': queues.count(),
            'waiting': queues.filter(status='waiting').count(),
            'serving': queues.filter(status='serving').count(),
            'completed': queues.filter(status='completed').count(),
            'cancelled': queues.filter(status='cancelled').count(),
        }
        
        # Get user appointments
        appointments = Appointment.objects.filter(user=user)
        appointment_statuses = {
            'total': appointments.count(),
            'pending': appointments.filter(status='pending').count(),
            'approved': appointments.filter(status='approved').count(),
            'rejected': appointments.filter(status='rejected').count(),
            'completed': appointments.filter(status='completed').count(),
            'cancelled': appointments.filter(status='cancelled').count(),
        }
        
        return {
            'user': user,
            'verification': verification,
            'queue_statuses': queue_statuses,
            'appointment_statuses': appointment_statuses,
            'message': f"Status verification completed for user {user.username}"
        }
    except User.DoesNotExist:
        return {
            'is_valid': False,
            'message': f"User with ID {user_id} not found"
        }
    except Exception as e:
        return {
            'is_valid': False,
            'message': f"Error verifying user statuses: {str(e)}"
        }
