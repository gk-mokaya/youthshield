# users/admin.py (enhanced with image preview)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'full_name',
        'user_type_badge',
        'phone_number',
        'profile_picture_preview',
        'is_active',
        'date_joined_short'
    )
    
    list_filter = ('user_type', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    list_editable = ('is_active',)
    
    fieldsets = (
        ('Authentication', {
            'fields': ('username', 'password', 'email')
        }),
        ('Personal Info', {
            'fields': (
                'first_name',
                'last_name',
                'phone_number',
                'address',
                'date_of_birth',
                'profile_picture',
                'profile_picture_preview'
            )
        }),
        ('Permissions', {
            'fields': (
                'user_type',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password1',
                'password2',
                'user_type',
                'is_staff',
                'is_active'
            ),
        }),
    )
    
    readonly_fields = (
        'last_login',
        'date_joined',
        'profile_picture_preview',
        'date_joined_short'
    )
    
    def full_name(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else "No Name"
    full_name.short_description = 'Full Name'
    
    def user_type_badge(self, obj):
        colors = {'user': 'blue', 'staff': 'green'}
        color = colors.get(obj.user_type, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold; padding: 2px 6px; border-radius: 3px; background-color: {}20;">{}</span>',
            color, color, obj.get_user_type_display().upper()
        )
    user_type_badge.short_description = 'User Type'
    
    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />',
                obj.profile_picture.url
            )
        return "No Image"
    profile_picture_preview.short_description = 'Profile Picture'
    
    def date_joined_short(self, obj):
        return obj.date_joined.strftime('%b %d, %Y')
    date_joined_short.short_description = 'Joined'
    
    # Make profile_picture_preview available in fieldsets
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj and obj.profile_picture:
            # Add preview to fieldsets for existing objects
            return fieldsets
        return fieldsets

admin.site.register(CustomUser, CustomUserAdmin)