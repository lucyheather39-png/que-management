from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('book/', views.book_appointment_view, name='book'),
    path('my-appointments/', views.my_appointments_view, name='my_appointments'),
    path('detail/<int:appointment_id>/', views.appointment_detail_view, name='detail'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment_view, name='cancel'),
]
