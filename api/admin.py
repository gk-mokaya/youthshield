from django.contrib import admin
from .models import APILog, APIKey

@admin.register(APILog)
class APILogAdmin(admin.ModelAdmin):
    list_display = ['endpoint', 'method', 'status_code', 'created_at', 'duration', 'ip_address']
    list_filter = ['method', 'status_code', 'created_at']
    search_fields = ['endpoint', 'ip_address']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'key', 'is_active', 'created_at', 'last_used']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'user__username', 'key']
    readonly_fields = ['key', 'created_at']