from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Appointment
from .forms import AppointmentForm

@login_required
def book_appointment_view(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            try:
                appointment = form.save_appointment(request.user)
                messages.success(request, 'Appointment booked successfully! Awaiting admin approval.')
                return redirect('appointments:my_appointments')
            except Exception as e:
                messages.error(request, f'Error booking appointment: {str(e)}')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AppointmentForm()
    
    context = {'form': form}
    return render(request, 'pages/appointments/book.html', context)

@login_required
def my_appointments_view(request):
    # Get all appointments for the user, ordered by most recent first
    appointments = Appointment.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'appointments': appointments,
    }
    return render(request, 'pages/appointments/my_appointments.html', context)

@login_required
def appointment_detail_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'pages/appointments/detail.html', context)

@login_required
def cancel_appointment_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    
    if appointment.status in ['pending', 'approved']:
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully.')
    else:
        messages.error(request, f'Cannot cancel appointment with status: {appointment.get_status_display()}')
    
    return redirect('appointments:my_appointments')
