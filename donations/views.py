from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from .models import Donation
from .forms import DonationForm
from .mpesa import initiate_stk_push, handle_mpesa_callback
from .paypal import create_paypal_order, capture_paypal_order
from .stripe_handler import create_stripe_payment_intent, handle_stripe_webhook

def donate(request):
    """Donation form page"""
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            
            if request.user.is_authenticated:
                donation.donor = request.user
                if not donation.donor_name:
                    donation.donor_name = f"{request.user.first_name} {request.user.last_name}"
                if not donation.donor_email:
                    donation.donor_email = request.user.email
            
            # Save the donation (this will generate transaction_id via save() method)
            donation.save()
            
            # Process based on payment method
            payment_method = form.cleaned_data['payment_method']
            
            if payment_method == 'mpesa':
                # Ensure phone number is provided for M-Pesa
                if not donation.donor_phone:
                    messages.error(request, 'Phone number is required for M-Pesa payments.')
                    return render(request, 'donations/donate.html', {'form': form})
                
                response = initiate_stk_push(
                    phone=donation.donor_phone,
                    amount=donation.amount,
                    account_reference=f"DON-{donation.id}",
                    description="Donation to NGO"
                )
                
                if response and response.get('ResponseCode') == '0':
                    # Update with M-Pesa transaction ID
                    donation.transaction_id = response.get('CheckoutRequestID')
                    donation.save()
                    return redirect('donations:payment_pending', donation_id=donation.id)
                else:
                    donation.status = 'failed'
                    donation.save()
                    error_msg = response.get('ResponseDescription') if response else 'Payment failed'
                    messages.error(request, f'Failed to initiate M-Pesa payment: {error_msg}')
                    return redirect('donations:donate')
                    
            elif payment_method == 'paypal':
                # Redirect to PayPal
                return redirect('donations:paypal_payment', donation_id=donation.id)
                
            elif payment_method == 'card':
                # Show card payment form
                return redirect('donations:card_payment', donation_id=donation.id)
                
    else:
        form = DonationForm()
        if request.user.is_authenticated:
            form.fields['donor_name'].initial = f"{request.user.first_name} {request.user.last_name}"
            form.fields['donor_email'].initial = request.user.email
    
    return render(request, 'donations/donate.html', {'form': form})

@login_required
def donation_history(request):
    """User donation history"""
    donations = Donation.objects.filter(donor=request.user).order_by('-created_at')
    return render(request, 'donations/history.html', {'donations': donations})

def payment_pending(request, donation_id):
    """Payment pending page"""
    donation = get_object_or_404(Donation, id=donation_id)
    return render(request, 'donations/payment_pending.html', {'donation': donation})

def donation_success(request, donation_id):
    """Payment success page"""
    donation = get_object_or_404(Donation, id=donation_id)
    return render(request, 'donations/payment_success.html', {'donation': donation})

def donation_failed(request, donation_id):
    """Payment failed page"""
    donation = get_object_or_404(Donation, id=donation_id)
    return render(request, 'donations/payment_failed.html', {'donation': donation})

def check_payment(request, donation_id):
    """Check payment status"""
    donation = get_object_or_404(Donation, id=donation_id)
    
    if donation.status == 'completed':
        return redirect('donations:success', donation_id=donation.id)
    elif donation.status == 'failed':
        return redirect('donations:failed', donation_id=donation.id)
    
    # Still pending
    return redirect('donations:payment_pending', donation_id=donation.id)

@csrf_exempt
def mpesa_callback(request):
    """M-Pesa callback endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            success = handle_mpesa_callback(data)
            
            if success:
                return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})
            else:
                return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Failed'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def paypal_payment(request, donation_id):
    """PayPal payment page"""
    donation = get_object_or_404(Donation, id=donation_id)
    
    # Create PayPal order
    order = create_paypal_order(
        amount=donation.amount,
        currency='USD',  # PayPal supports USD, not KES
        return_url=f"{settings.BASE_URL}/donations/paypal-success/{donation.id}/",
        cancel_url=f"{settings.BASE_URL}/donations/paypal-cancel/{donation.id}/"
    )
    
    if order:
        donation.transaction_id = order.get('id')
        donation.save()
        
        # Find approval URL
        approval_url = None
        for link in order.get('links', []):
            if link.get('rel') == 'approve':
                approval_url = link.get('href')
                break
        
        if approval_url:
            return redirect(approval_url)
    
    messages.error(request, 'Failed to create PayPal order.')
    return redirect('donations:donate')

def paypal_success(request, donation_id):
    """PayPal success callback"""
    donation = get_object_or_404(Donation, id=donation_id)
    order_id = request.GET.get('token') or request.GET.get('order_id')
    
    if order_id:
        # Capture the payment
        result = capture_paypal_order(order_id)
        if result and result.get('status') == 'COMPLETED':
            donation.status = 'completed'
            donation.save()
            return redirect('donations:success', donation_id=donation.id)
    
    donation.status = 'failed'
    donation.save()
    messages.error(request, 'PayPal payment failed.')
    return redirect('donations:failed', donation_id=donation.id)

def paypal_cancel(request, donation_id):
    """PayPal cancel callback"""
    donation = get_object_or_404(Donation, id=donation_id)
    donation.status = 'cancelled'
    donation.save()
    
    messages.info(request, 'PayPal payment was cancelled.')
    return redirect('donations:donate')

def card_payment(request, donation_id):
    """Card payment page"""
    donation = get_object_or_404(Donation, id=donation_id)
    
    # Create Stripe payment intent
    intent = create_stripe_payment_intent(
        amount=donation.amount,
        currency=donation.currency.lower(),
        metadata={
            'donation_id': donation.id,
            'donor_email': donation.donor_email
        }
    )
    
    if intent:
        donation.transaction_id = intent.get('id')
        donation.save()
        
        context = {
            'donation': donation,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'client_secret': intent.get('client_secret'),
        }
        return render(request, 'donations/card_payment.html', context)
    
    messages.error(request, 'Failed to initialize card payment.')
    return redirect('donations:donate')

@csrf_exempt
def stripe_webhook(request):
    """Stripe webhook endpoint"""
    if request.method == 'POST':
        try:
            payload = request.body
            sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

            # Verify webhook signature and process
            result = handle_stripe_webhook(payload, sig_header)
            if result is True:
                return JsonResponse({'status': 'success'})
            elif result is False:
                return JsonResponse({'status': 'failed'}, status=400)
            else:
                return JsonResponse({'status': 'received'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid method'}, status=400)

@login_required
def receipt(request, donation_id):
    """Generate donation receipt"""
    from core.models import WebsiteSetting
    donation = get_object_or_404(Donation, id=donation_id, donor=request.user, status='completed')
    website_settings = WebsiteSetting.objects.first()
    return render(request, 'donations/receipt.html', {
        'donation': donation,
        'website_settings': website_settings
    })

def process_payment(request, donation_id, method):
    """Process payment (legacy endpoint)"""
    donation = get_object_or_404(Donation, id=donation_id)

    if method == 'paypal':
        return redirect('donations:paypal_payment', donation_id=donation.id)
    elif method == 'card':
        return redirect('donations:card_payment', donation_id=donation.id)
    elif method == 'mpesa':
        # Already handled in donate view
        return redirect('donations:payment_pending', donation_id=donation.id)

    messages.error(request, 'Invalid payment method.')
    return redirect('donations:donate')
