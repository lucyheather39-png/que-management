from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Queue, Service
from .forms import QueueCreationForm, ServiceCreationForm
from .utils import generate_queue_number, assign_priority, calculate_position

@login_required
def dashboard_view(request):
    try:
        from apps.appointments.models import Appointment
        
        user_queues = Queue.objects.filter(user=request.user, date=timezone.now().date())
        active_queue = user_queues.filter(status__in=['waiting', 'serving']).first()
        
        # Get user's pending and approved appointments
        user_appointments = Appointment.objects.filter(
            user=request.user,
            status__in=['pending', 'approved']
        ).order_by('-created_at')[:5]
        
        context = {
            'user_queues': user_queues,
            'active_queue': active_queue,
            'user_appointments': user_appointments,
        }
        return render(request, 'pages/queue/dashboard.html', context)
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return redirect('security:login')

@login_required
def take_queue_view(request):
    if request.method == 'POST':
        form = QueueCreationForm(request.POST)
        if form.is_valid():
            service = form.cleaned_data['service']
            
            # Check if user already has an active queue
            active_queue = Queue.objects.filter(
                user=request.user,
                status__in=['waiting', 'serving'],
                date=timezone.now().date()
            ).exists()
            
            if active_queue:
                messages.warning(request, 'You already have an active queue. Complete it first.')
                return redirect('queues:take_queue')
            
            try:
                # Ensure user has a profile
                from apps.accounts.models import UserProfile
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                
                # Get priority from user profile
                priority_level = profile.get_priority_level()
                queue_number = generate_queue_number(service)
                position = calculate_position(service, priority_level)
                
                queue = Queue.objects.create(
                    user=request.user,
                    service=service,
                    queue_number=queue_number,
                    priority_level=priority_level,
                    position_in_queue=position,
                    date=timezone.now().date()
                )
                
                messages.success(request, f'Queue number {queue.queue_number} assigned! Your position: #{position}')
                return redirect('queues:queue_detail', queue_id=queue.id)
            except Exception as e:
                messages.error(request, f'Error creating queue: {str(e)}')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = QueueCreationForm()
    
    context = {'form': form}
    return render(request, 'pages/queue/take_queue.html', context)

@login_required
def queue_detail_view(request, queue_id):
    queue = get_object_or_404(Queue, id=queue_id, user=request.user)
    
    context = {
        'queue': queue,
    }
    return render(request, 'pages/queue/queue_detail.html', context)

@login_required
def queue_list_view(request):
    user_queues = Queue.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'queues': user_queues,
    }
    return render(request, 'pages/queue/queue_list.html', context)

@login_required
def cancel_queue_view(request, queue_id):
    queue = get_object_or_404(Queue, id=queue_id, user=request.user)
    
    if queue.status == 'waiting':
        queue.status = 'cancelled'
        queue.save()
        messages.success(request, 'Queue cancelled successfully.')
    else:
        messages.error(request, 'Cannot cancel queue that is already being served.')
    
    return redirect('queues:dashboard')

def is_admin(user):
    return user.is_staff and user.is_superuser

@login_required
@user_passes_test(is_admin)
def add_service_view(request):
    """Add a new service to the system"""
    if request.method == 'POST':
        form = ServiceCreationForm(request.POST)
        if form.is_valid():
            try:
                service = form.save()
                messages.success(request, f'Service "{service.name}" created successfully!')
                return redirect('queues:service_list')
            except Exception as e:
                messages.error(request, f'Error creating service: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ServiceCreationForm()
    
    context = {
        'form': form,
        'title': 'Add New Service'
    }
    return render(request, 'pages/admin/add_service.html', context)

@login_required
@user_passes_test(is_admin)
def service_list_view(request):
    """View all services"""
    services = Service.objects.all().order_by('name')
    
    context = {
        'services': services,
    }
    return render(request, 'pages/admin/service_list.html', context)

@login_required
@user_passes_test(is_admin)
def edit_service_view(request, service_id):
    """Edit an existing service"""
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        form = ServiceCreationForm(request.POST, instance=service)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Service "{service.name}" updated successfully!')
                return redirect('queues:service_list')
            except Exception as e:
                messages.error(request, f'Error updating service: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ServiceCreationForm(instance=service)
    
    context = {
        'form': form,
        'service': service,
        'title': f'Edit Service: {service.name}'
    }
    return render(request, 'pages/admin/edit_service.html', context)

@login_required
@user_passes_test(is_admin)
def delete_service_view(request, service_id):
    """Delete a service"""
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        try:
            service_name = service.name
            service.delete()
            messages.success(request, f'Service "{service_name}" deleted successfully!')
            return redirect('queues:service_list')
        except Exception as e:
            messages.error(request, f'Error deleting service: {str(e)}')
    
    context = {
        'service': service,
    }
    return render(request, 'pages/admin/delete_service_confirm.html', context)
