from django.utils import timezone
from django.db.models import Count, Q, Max
from .models import Queue

def generate_queue_number(service):
    today = timezone.now().date()
    today_count = Queue.objects.filter(
        service=service,
        date=today
    ).count() + 1
    
    queue_number = f"{service.code.upper()}-{today.strftime('%d%m%y')}-{today_count:04d}"
    return queue_number

def assign_priority(user_profile):
    """Assign priority level based on citizen type"""
    return user_profile.get_priority_level()

def calculate_position(service, priority_level):
    """Calculate position in queue based on priority and service"""
    today = timezone.now().date()
    
    # Count people with higher priority ahead
    ahead_count = Queue.objects.filter(
        service=service,
        date=today,
        status__in=['waiting', 'serving'],
        priority_level__lt=priority_level
    ).count()
    
    # Count people with same priority ahead
    same_priority = Queue.objects.filter(
        service=service,
        date=today,
        status__in=['waiting', 'serving'],
        priority_level=priority_level
    ).count()
    
    return ahead_count + same_priority + 1

def get_queue_statistics():
    """Get overall queue statistics"""
    today = timezone.now().date()
    return {
        'total_today': Queue.objects.filter(date=today).count(),
        'waiting': Queue.objects.filter(date=today, status='waiting').count(),
        'serving': Queue.objects.filter(date=today, status='serving').count(),
        'completed': Queue.objects.filter(date=today, status='completed').count(),
    }
