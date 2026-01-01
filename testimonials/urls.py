from django.urls import path
from . import views

app_name = 'testimonials'

urlpatterns = [
    path('add/', views.add_testimonial, name='add_testimonial'),
    path('edit/<int:testimonial_id>/', views.edit_testimonial, name='edit_testimonial'),
    path('delete/<int:testimonial_id>/', views.delete_testimonial, name='delete_testimonial'),
]
