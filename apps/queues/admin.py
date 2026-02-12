from django.contrib import admin
from .models import Service, Queue

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'service_type', 'estimated_time', 'is_active')
    list_filter = ('service_type', 'is_active')
    search_fields = ('name', 'code')

@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ('queue_number', 'user', 'service', 'status', 'priority_level', 'created_at')
    list_filter = ('status', 'date', 'service', 'priority_level')
    search_fields = ('queue_number', 'user__username')
    readonly_fields = ('queue_number', 'created_at')
