from django.contrib import admin
from django.utils.html import format_html
from .models import WebsiteSetting, CoreValue, BoardMember, ExecutiveCommittee

# Custom actions
@admin.action(description='Activate selected items')
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)

@admin.action(description='Deactivate selected items')
def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)

@admin.register(WebsiteSetting)
class WebsiteSettingAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'Registration_Number')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'logo', 'Registration_Number')
        }),
        ('Color Scheme', {
            'fields': ('primary_color', 'secondary_color', 'accent_color')
        }),
        ('Organization Details', {
            'fields': ('mission', 'vision')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('Social Media Links', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'tiktok_url', 'whatsapp_channel_url')
        }),
        ('Additional Information', {
            'fields': ('website_url', 'emergency_phone', 'support_email', 'tagline', 'copyright_text', 'description'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return not WebsiteSetting.objects.exists()

@admin.register(CoreValue)
class CoreValueAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_class', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    list_editable = ('order', 'is_active')
    ordering = ('order',)
    actions = [make_active, make_inactive]

@admin.register(BoardMember)
class BoardMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'order', 'is_active', 'photo_preview')
    list_filter = ('is_active', 'position')
    search_fields = ('name', 'position', 'bio')
    list_editable = ('order', 'is_active')
    ordering = ('order',)
    actions = [make_active, make_inactive]
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;" />', obj.photo.url)
        return "No Photo"
    photo_preview.short_description = 'Photo'

@admin.register(ExecutiveCommittee)
class ExecutiveCommitteeAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'display_order', 'is_active', 'photo_preview')
    list_filter = ('is_active', 'position')
    search_fields = ('name', 'position', 'bio')
    list_editable = ('display_order', 'is_active')
    ordering = ('display_order',)
    actions = [make_active, make_inactive]
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;" />', obj.photo.url)
        return "No Photo"
    photo_preview.short_description = 'Photo'