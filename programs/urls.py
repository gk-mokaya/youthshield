from django.urls import path
from . import views

app_name = 'programs'

urlpatterns = [
    path('', views.program_list, name='program_list'),
    path('<int:program_id>/', views.program_detail, name='program_detail'),
    path('<int:program_id>/modal/', views.program_modal, name='program_modal'),
    path('add/', views.add_program, name='add_program'),
    path('edit/<int:program_id>/', views.edit_program, name='edit_program'),
    path('toggle/<int:program_id>/', views.toggle_program, name='toggle_program'),
    path('services/add/', views.add_service, name='add_service'),
    path('objectives/add/', views.add_objective, name='add_objective'),
]
