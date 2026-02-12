from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'citizen_type', 'is_verified', 'created_at')
    list_filter = ('citizen_type', 'is_verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'id_number')
    readonly_fields = ('created_at', 'updated_at')
