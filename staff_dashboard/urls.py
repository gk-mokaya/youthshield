from django.urls import path

from . import views

app_name = 'staff_dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('chart-data/', views.dashboard_chart_data, name='dashboard_chart_data'),
    path('users/', views.manage_users, name='manage_users'),
    path('donations/', views.manage_donations, name='manage_donations'),
    path('programs/', views.manage_programs, name='manage_programs'),
    path('testimonials/', views.manage_testimonials, name='manage_testimonials'),
    path('contact-messages/', views.manage_contact_messages, name='manage_contact_messages'),
    path('backups/', views.manage_backups, name='manage_backups'),
    # AJAX URLs
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/get/', views.get_user, name='get_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('donations/<int:donation_id>/edit/', views.edit_donation, name='edit_donation'),
    path('donations/<int:donation_id>/get/', views.get_donation, name='get_donation'),
    path('programs/create/', views.create_program, name='create_program'),
    path('programs/<int:program_id>/get/', views.get_program, name='get_program'),
    path('programs/<int:program_id>/edit/', views.edit_program, name='edit_program'),
    path('programs/<int:program_id>/delete/', views.delete_program, name='delete_program'),
    path('testimonials/<int:testimonial_id>/edit/', views.edit_testimonial, name='edit_testimonial'),
    path('testimonials/<int:testimonial_id>/get/', views.get_testimonial, name='get_testimonial'),
    path('testimonials/<int:testimonial_id>/approve/', views.approve_testimonial, name='approve_testimonial'),
    path('testimonials/<int:testimonial_id>/reject/', views.reject_testimonial, name='reject_testimonial'),
    path('testimonials/<int:testimonial_id>/delete/', views.delete_testimonial, name='delete_testimonial'),
    path('contact-messages/<int:message_id>/get/', views.get_contact_message, name='get_contact_message'),
    path('contact-messages/<int:message_id>/reply/', views.reply_contact_message, name='reply_contact_message'),
    path('contact-messages/<int:message_id>/edit/', views.edit_contact_message, name='edit_contact_message'),
    path('contact-messages/<int:message_id>/delete/', views.delete_contact_message, name='delete_contact_message'),
    path('backups/create/', views.create_backup, name='create_backup'),
    path('backups/<str:backup_id>/delete/', views.delete_backup, name='delete_backup'),
    path('backups/<str:backup_id>/download/', views.download_backup, name='download_backup'),
    path('backups/save-auto-backup-settings/', views.save_auto_backup_settings, name='save_auto_backup_settings'),
]
