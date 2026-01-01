from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # M-Pesa endpoints
    path('mpesa/stk-push/', views.initiate_mpesa_stk_push, name='mpesa_stk_push'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    
    # PayPal endpoints
    path('paypal/create-order/', views.create_paypal_order, name='create_paypal_order'),
    path('paypal/capture-order/<str:order_id>/', views.capture_paypal_order, name='capture_paypal_order'),
    path('paypal/success/', views.paypal_success, name='paypal_success'),
    path('paypal/cancel/', views.paypal_cancel, name='paypal_cancel'),
    
    # Stripe endpoints
    path('stripe/create-payment-intent/', views.create_stripe_payment_intent, name='stripe_payment_intent'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    
    # Donation endpoints
    path('donations/stats/', views.donation_stats, name='donation_stats'),
    
    # Content endpoints
    path('programs/', views.program_list, name='program_list'),
    path('events/', views.event_list, name='event_list'),
]