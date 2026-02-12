from django.urls import path
from . import views

app_name = 'admin_management'

urlpatterns = [
    # Public setup - create first admin
    path('setup/', views.setup_first_admin, name='setup_first_admin'),
    # Protected admin views
    path('', views.admin_dashboard_view, name='dashboard'),
    path('verifications/pending/', views.pending_verifications_view, name='pending_verifications'),
    path('verifications/pending/approve-all/', views.approve_all_pending_verifications_view, name='approve_all_pending_verifications'),
    path('verifications/<int:verification_id>/approve/', views.approve_verification_view, name='approve_verification'),
    path('verifications/<int:verification_id>/approve-quick/', views.approve_single_verification_view, name='approve_single_verification'),
    path('appointments/pending/', views.pending_appointments_view, name='pending_appointments'),
    path('appointments/<int:appointment_id>/manage/', views.manage_appointment_view, name='manage_appointment'),
    path('queue/management/', views.queue_management_view, name='queue_management'),
    path('queue/<int:queue_id>/update/', views.update_queue_status_view, name='update_queue_status'),
    path('queue/<int:queue_id>/delete/', views.delete_queue_view, name='delete_queue'),
    path('users/', views.users_management_view, name='users_management'),
    path('user/<int:user_profile_id>/status/', views.check_account_status_view, name='check_account_status'),
    path('profile/<int:user_profile_id>/verify/', views.verify_user_profile_view, name='verify_user_profile'),
    path('profile/<int:user_profile_id>/unverify/', views.unverify_user_profile_view, name='unverify_user_profile'),
    path('logs/', views.admin_logs_view, name='logs'),
    path('logs/<int:log_id>/delete/', views.delete_log_view, name='delete_log'),
    path('admin/create/', views.create_admin_view, name='create_admin'),
    path('admin/<int:admin_id>/delete/', views.delete_admin_view, name='delete_admin'),
    # Status Verification URLs
    path('verify/user/<int:user_id>/', views.verify_user_status_view, name='verify_user_status'),
    path('verify/all-statuses/<int:user_id>/', views.verify_all_user_statuses_view, name='verify_all_user_statuses'),
    # Profile Verification URLs
    path('verification/stats/', views.profile_verification_stats_view, name='verification_stats'),
    path('profile/<int:user_profile_id>/approve/', views.quick_approve_profile_view, name='quick_approve_profile'),
    path('profile/<int:user_profile_id>/reject/', views.quick_reject_profile_view, name='quick_reject_profile'),
    path('profile/<int:user_profile_id>/status/', views.get_profile_verification_status_view, name='profile_verification_status'),
    # User Verification URLs
    path('users/verification/stats/', views.user_verification_stats_view, name='user_verification_stats'),
    path('users/unverified/', views.unverified_users_view, name='unverified_users'),
    path('users/verified/', views.verified_users_view, name='verified_users'),
    path('users/inactive/', views.inactive_users_view, name='inactive_users'),
    path('user/<int:user_id>/verify/', views.verify_user_account_view, name='verify_user_account'),
    path('user/<int:user_id>/deactivate/', views.deactivate_user_account_view, name='deactivate_user_account'),
    path('user/<int:user_id>/verification-status/', views.user_verification_status_view, name='user_verification_status'),
    # Walk-in Queues
    path('walkin-queues/', views.walkin_queues_view, name='walkin_queues'),
    path('walkin-queues/reset/', views.reset_walkin_queues_view, name='reset_walkin_queues'),
    path('api/walkin-queues/', views.get_walkin_queues_api, name='api_walkin_queues'),
]