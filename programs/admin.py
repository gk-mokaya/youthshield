from django.contrib import admin
from .models import Program, Service, Objective

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('is_active',)
    # Removed prepopulated_fields since slug field doesn't exist
    # If you want slugs, add this to your Program model first:
    # slug = models.SlugField(max_length=200, unique=True, blank=True)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'image')
        }),
        ('Program Details', {
            'fields': ('objectives', 'target_audience', 'duration')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon_class', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    list_editable = ('order', 'is_active')
    ordering = ('order',)

@admin.register(Objective)
class ObjectiveAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon_class', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    list_editable = ('order', 'is_active')
    ordering = ('order',)