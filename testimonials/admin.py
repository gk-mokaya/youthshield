# testimonials/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Testimonial

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = (
        'user_display',
        'rating_stars',
        'truncated_content',
        'status',
        'created_at',
        'reviewed_by_display'
    )
    list_filter = ('status', 'rating', 'created_at')
    search_fields = (
        'user__username',
        'user__first_name', 
        'user__last_name',
        'user__email',
        'content'
    )
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at', 'reviewed_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Testimonial Content', {
            'fields': (
                'user',
                'content',
                'rating',
                'status'
            )
        }),
        ('Review Information', {
            'fields': (
                'reviewed_by',
                'reviewed_at',
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    # Custom methods for display
    def user_display(self, obj):
        """Display user's full name or username"""
        if obj.user.get_full_name():
            return f"{obj.user.get_full_name()} ({obj.user.username})"
        return obj.user.username
    user_display.short_description = 'User'
    
    def rating_stars(self, obj):
        """Display rating as stars"""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(
            '<span style="color: gold; font-size: 16px;">{}</span>',
            stars
        )
    rating_stars.short_description = 'Rating'
    
    def truncated_content(self, obj):
        """Display truncated content for better list view"""
        if len(obj.content) > 100:
            return f"{obj.content[:100]}..."
        return obj.content
    truncated_content.short_description = 'Content'
    
    def reviewed_by_display(self, obj):
        """Display reviewer information"""
        if obj.reviewed_by:
            return obj.reviewed_by.get_full_name() or obj.reviewed_by.username
        return "Not reviewed"
    reviewed_by_display.short_description = 'Reviewed By'
    
    # Custom actions
    actions = ['approve_testimonials', 'reject_testimonials', 'mark_pending']
    
    @admin.action(description='Approve selected testimonials')
    def approve_testimonials(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} testimonials approved successfully.')
    
    @admin.action(description='Reject selected testimonials')
    def reject_testimonials(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} testimonials rejected.')
    
    @admin.action(description='Mark selected as pending review')
    def mark_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} testimonials marked as pending.')
    
    def save_model(self, request, obj, form, change):
        """Automatically set reviewed_by when status changes from pending"""
        if change and 'status' in form.changed_data and obj.status != 'pending':
            if not obj.reviewed_by:
                obj.reviewed_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Optimize queryset by selecting related users"""
        return super().get_queryset(request).select_related('user', 'reviewed_by')