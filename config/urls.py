from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from apps.admin_management.views import public_walkin_queue_view

def redirect_to_dashboard(request):
    # Check if any admin exists
    admin_exists = User.objects.filter(is_staff=True, is_superuser=True).exists()
    
    if not admin_exists:
        # No admin - redirect to setup page
        return HttpResponseRedirect('/admin-panel/setup/')
    
    if request.user.is_authenticated:
        if request.user.is_staff and request.user.is_superuser:
            return HttpResponseRedirect('/admin-panel/')
        return HttpResponseRedirect('/queue/dashboard/')  # Changed from '/queue/'
    return HttpResponseRedirect('/auth/login/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', TemplateView.as_view(template_name='pages/index.html'), name='home'),
    path('walkin-queue/', public_walkin_queue_view, name='public_walkin_queue'),
    path('', redirect_to_dashboard, name='home_redirect'),
    path('auth/', include('apps.security.urls')),
    path('queue/', include('apps.queues.urls')),
    path('appointment/', include('apps.appointments.urls')),
    path('admin-panel/', include('apps.admin_management.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
