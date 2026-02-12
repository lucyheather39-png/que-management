from django.urls import path
from . import views

app_name = 'security'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-email/<int:user_id>/', views.verify_email_view, name='verify_email'),
    path('reset-password/<int:user_id>/', views.reset_password_view, name='reset_password'),
]
