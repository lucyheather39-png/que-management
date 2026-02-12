from django.contrib import admin
from .models import VerificationRequest, AdminLog

@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at', 'reviewed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'reviewed_at')

@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ('admin', 'action', 'timestamp')
    list_filter = ('admin', 'timestamp')
    search_fields = ('action', 'description')
    readonly_fields = ('timestamp',)
