from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    path('', views.donate, name='donate'),
    path('process/<int:donation_id>/<str:method>/', views.process_payment, name='process_payment'),
    path('success/<int:donation_id>/', views.donation_success, name='success'),
    path('failed/<int:donation_id>/', views.donation_failed, name='failed'),
    path('pending/<int:donation_id>/', views.payment_pending, name='payment_pending'),
    path('check/<int:donation_id>/', views.check_payment, name='check_payment'),
    path('history/', views.donation_history, name='history'),
    path('mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
    path('paypal-payment/<int:donation_id>/', views.paypal_payment, name='paypal_payment'),
    path('paypal-success/<int:donation_id>/', views.paypal_success, name='paypal_success'),
    path('paypal-cancel/<int:donation_id>/', views.paypal_cancel, name='paypal_cancel'),
    path('card-payment/<int:donation_id>/', views.card_payment, name='card_payment'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('receipt/<int:donation_id>/', views.receipt, name='receipt'),
]
