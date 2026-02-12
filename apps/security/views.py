from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from apps.accounts.forms import UserRegistrationForm, UserProfileForm
from apps.accounts.models import UserProfile, EmailVerificationCode

def send_verification_email(email, verification_code):
    """Send verification code via email"""
    try:
        subject = 'Password Reset Verification Code'
        message = f'''
Hello,

Your password reset verification code is: {verification_code}

This code will expire in 10 minutes.

If you did not request a password reset, please ignore this email.

Best regards,
Queue Management System
        '''
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        return True
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return False

def register_view(request):
    if request.user.is_authenticated:
        return redirect('/queue/dashboard/')  # Changed to direct URL
    
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('/auth/login/')  # Changed to direct URL
        else:
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'pages/auth/register.html', context)

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff and request.user.is_superuser:
            return redirect('/admin-panel/')  # Changed to direct URL
        return redirect('/queue/dashboard/')  # Changed to direct URL
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            
            # Redirect based on user role
            if user.is_staff and user.is_superuser:
                return redirect('/admin-panel/')
            return redirect('/queue/dashboard/')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'pages/auth/login.html')

@login_required(login_url='security:login')
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/auth/login/')  # Changed to direct URL

@login_required
def profile_view(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('/auth/profile/')  # Changed to direct URL
    else:
        form = UserProfileForm(instance=profile)
    
    context = {'form': form, 'profile': profile}
    return render(request, 'pages/auth/profile.html', context)

def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect('queues:dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Create verification code
            verification = EmailVerificationCode.create_verification_code(user, email)
            
            # Send verification email
            email_sent = send_verification_email(email, verification.verification_code)
            
            if email_sent:
                messages.success(request, f'Verification code sent to {email}.')
            else:
                # Fallback: Show code in development/testing
                messages.warning(request, f'Verification code: {verification.verification_code}. (Email not configured. For testing: {verification.verification_code})')
            
            # Redirect to verification code page
            return redirect('security:verify_email', user_id=user.id)
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
        except User.MultipleObjectsReturned:
            messages.error(request, 'Multiple accounts found with this email. Please contact support.')
    
    return render(request, 'pages/auth/forgot_password.html')

def verify_email_view(request, user_id):
    if request.user.is_authenticated:
        return redirect('queues:dashboard')
    
    try:
        user = User.objects.get(pk=user_id)
        verification = EmailVerificationCode.objects.get(user=user)
    except (User.DoesNotExist, EmailVerificationCode.DoesNotExist):
        messages.error(request, 'Invalid request.')
        return redirect('security:login')
    
    if verification.is_expired():
        messages.error(request, 'Verification code has expired. Please try again.')
        return redirect('security:forgot_password')
    
    if request.method == 'POST':
        code = request.POST.get('verification_code')
        
        if code == verification.verification_code:
            verification.is_used = True
            verification.save()
            return redirect('security:reset_password', user_id=user.id)
        else:
            messages.error(request, 'Invalid verification code.')
    
    return render(request, 'pages/auth/verify_email.html', {
        'email': verification.email,
        'user_id': user.id
    })

def reset_password_view(request, user_id):
    if request.user.is_authenticated:
        return redirect('queues:dashboard')
    
    try:
        user = User.objects.get(pk=user_id)
        verification = EmailVerificationCode.objects.get(user=user)
    except (User.DoesNotExist, EmailVerificationCode.DoesNotExist):
        messages.error(request, 'Invalid request.')
        return redirect('security:login')
    
    if not verification.is_used:
        messages.error(request, 'Please verify your email first.')
        return redirect('security:forgot_password')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        else:
            user.set_password(password)
            user.save()
            verification.delete()
            messages.success(request, 'Password has been reset successfully. Please login.')
            return redirect('security:login')
    
    return render(request, 'pages/auth/reset_password.html', {'user_id': user.id})
