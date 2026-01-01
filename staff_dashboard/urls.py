from django.urls import path
from . import views

app_name = 'staff_dashboard'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('analytics-data/', views.analytics_data, name='analytics_data'),

    # User Management
    path('users/', views.user_management, name='user_management'),
    path('users/create/', views.create_user, name='create_user'),
    path('add-staff/', views.create_user, name='add_staff'),
    path('staff-roles/', views.user_management, name='staff_roles'),
    path('users/<int:user_id>/view/', views.user_management, name='view_staff'),
    path('users/<int:user_id>/edit/', views.user_management, name='edit_staff'),
    path('users/<int:user_id>/update/', views.update_user, name='update_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('staff-reports/', views.dashboard, name='staff_reports'),
    path('staff-settings/', views.website_settings, name='staff_settings'),

    # Website Settings
    path('settings/', views.website_settings, name='website_settings'),

    # Core Values
    path('core-values/', views.core_values_management, name='core_values'),
    path('core-values/create/', views.create_core_value, name='create_core_value'),
    path('core-values/<int:value_id>/update/', views.update_core_value, name='update_core_value'),
    path('core-values/<int:value_id>/toggle/', views.toggle_core_value, name='toggle_core_value'),
    path('core-values/<int:value_id>/delete/', views.delete_core_value, name='delete_core_value'),

    # Board Members
    path('board-members/', views.board_members_management, name='board_members'),
    path('board-members/create/', views.create_board_member, name='create_board_member'),
    path('board-members/<int:member_id>/update/', views.update_board_member, name='update_board_member'),
    path('board-members/<int:member_id>/toggle/', views.toggle_board_member, name='toggle_board_member'),
    path('board-members/<int:member_id>/delete/', views.delete_board_member, name='delete_board_member'),

    # Executive Committee
    path('executive-committee/', views.executive_committee_management, name='executive_committee'),
    path('executive-committee/create/', views.create_executive_member, name='create_executive_member'),
    path('executive-committee/<int:member_id>/update/', views.update_executive_member, name='update_executive_member'),
    path('executive-committee/<int:member_id>/toggle/', views.toggle_executive_member, name='toggle_executive_member'),
    path('executive-committee/<int:member_id>/delete/', views.delete_executive_member, name='delete_executive_member'),

    # Contact Messages
    path('contact-messages/', views.contact_messages_management, name='contact_messages'),
    path('contact-messages/<int:message_id>/view/', views.view_message, name='view_message'),
    path('contact-messages/<int:message_id>/seen/', views.mark_message_seen, name='mark_message_seen'),
    path('contact-messages/<int:message_id>/resolved/', views.mark_message_resolved, name='mark_message_resolved'),
    path('contact-messages/<int:message_id>/delete/', views.delete_message, name='delete_message'),

    # Programs
    path('programs/', views.programs_management, name='programs'),
    path('programs/create/', views.create_program, name='create_program'),
    path('programs/<int:program_id>/update/', views.update_program, name='update_program'),
    path('programs/<int:program_id>/toggle/', views.toggle_program, name='toggle_program'),
    path('programs/<int:program_id>/delete/', views.delete_program, name='delete_program'),

    # Testimonials
    path('testimonials/', views.testimonials_management, name='testimonials'),
    path('testimonials/<int:testimonial_id>/approve/', views.approve_testimonial, name='approve_testimonial'),
    path('testimonials/<int:testimonial_id>/reject/', views.reject_testimonial, name='reject_testimonial'),
    path('testimonials/<int:testimonial_id>/delete/', views.delete_testimonial, name='delete_testimonial'),

    # Donations
    path('donations/', views.donations_management, name='donations'),
    path('donations/<int:donation_id>/view/', views.view_donation, name='view_donation'),
    path('donations/<int:donation_id>/generate-receipt/', views.generate_receipt, name='generate_receipt'),
    path('donations/export/', views.export_donations, name='export_donations'),

    # Backup
    path('backup/', views.backup_management, name='backup'),
]
