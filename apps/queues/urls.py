from django.urls import path
from . import views

app_name = 'queues'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('take/', views.take_queue_view, name='take_queue'),
    path('detail/<int:queue_id>/', views.queue_detail_view, name='queue_detail'),
    path('list/', views.queue_list_view, name='queue_list'),
    path('cancel/<int:queue_id>/', views.cancel_queue_view, name='cancel_queue'),
    
    # Service management
    path('service/add/', views.add_service_view, name='add_service'),
    path('service/list/', views.service_list_view, name='service_list'),
    path('service/<int:service_id>/edit/', views.edit_service_view, name='edit_service'),
    path('service/<int:service_id>/delete/', views.delete_service_view, name='delete_service'),
]
