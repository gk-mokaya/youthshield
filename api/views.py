from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import requests
import base64
import json
from datetime import datetime
import stripe
from .models import APILog
from donations.models import Donation

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def log_api_request(endpoint, method, request_data, response_data, status_code, ip_address, user_agent, duration):
    """Log API requests"""
    APILog.objects.create(
        endpoint=endpoint,
        method=method,
        request_data=request_data,
        response_data=response_data,
        status_code=status_code,
        ip_address=ip_address,
        user_agent=user_agent,
        duration=duration
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def initiate_mpesa_stk_push(request):
    """
    Initiate M-Pesa STK Push
    """
    start_time = datetime.now()
    
    phone = request.data.get('phone')
    amount = request.data.get('amount')
    account_ref = request.data.get('account_reference', 'DONATION')
    
    # Get access token
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    auth = base64.b64encode(f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}".encode()).decode()
    
    headers = {'Authorization': f'Basic {auth}'}
    
    try:
        # Get access token
        token_response = requests.get(auth_url, headers=headers, timeout=30)
        token_response.raise_for_status()
        access_token = token_response.json().get('access_token')
        
        # Prepare STK Push
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()
        ).decode()
        
        stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        stk_headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        stk_payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": str(int(amount)),
            "PartyA": phone,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": f"{settings.BASE_URL}/api/mpesa-callback/",
            "AccountReference": account_ref,
            "TransactionDesc": "Donation"
        }
        
        stk_response = requests.post(stk_url, json=stk_payload, headers=stk_headers, timeout=30)
        stk_response.raise_for_status()
        data = stk_response.json()
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        # Log the request
        log_api_request(
            endpoint='/api/mpesa/stk-push/',
            method='POST',
            request_data={'phone': phone, 'amount': amount, 'account_reference': account_ref},
            response_data=data,
            status_code=200,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            duration=duration
        )
        
        return Response({
            'success': True,
            'checkout_request_id': data.get('CheckoutRequestID'),
            'merchant_request_id': data.get('MerchantRequestID'),
            'response_code': data.get('ResponseCode'),
            'message': data.get('ResponseDescription')
        })
        
    except requests.exceptions.RequestException as e:
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        log_api_request(
            endpoint='/api/mpesa/stk-push/',
            method='POST',
            request_data={'phone': phone, 'amount': amount, 'account_reference': account_ref},
            response_data={'error': str(e)},
            status_code=400,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            duration=duration
        )
        
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def mpesa_callback(request):
    """
    Handle M-Pesa callback
    """
    try:
        data = request.data
        
        # Process callback data
        result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
        result_desc = data.get('Body', {}).get('stkCallback', {}).get('ResultDesc')
        checkout_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
        
        # Log callback
        log_api_request(
            endpoint='/api/mpesa/callback/',
            method='POST',
            request_data=data,
            response_data={'result_code': result_code, 'result_desc': result_desc},
            status_code=200,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            duration=0
        )
        
        # Update donation status based on result code
        if result_code == 0:
            # Success - Update donation as completed
            try:
                donation = Donation.objects.get(transaction_id=checkout_id)
                donation.status = 'completed'
                donation.save()
            except Donation.DoesNotExist:
                pass
        
        return Response({'ResultCode': 0, 'ResultDesc': 'Success'})
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_paypal_order(request):
    """
    Create PayPal order
    """
    start_time = datetime.now()
    
    amount = request.data.get('amount')
    currency = request.data.get('currency', 'USD')
    
    paypal_url = "https://api-m.sandbox.paypal.com/v2/checkout/orders"
    auth = base64.b64encode(f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_SECRET}".encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": currency,
                "value": str(amount)
            }
        }],
        "application_context": {
            "return_url": f"{settings.BASE_URL}/api/paypal/success/",
            "cancel_url": f"{settings.BASE_URL}/api/paypal/cancel/"
        }
    }
    
    try:
        response = requests.post(paypal_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        log_api_request(
            endpoint='/api/paypal/create-order/',
            method='POST',
            request_data={'amount': amount, 'currency': currency},
            response_data=data,
            status_code=200,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            duration=duration
        )
        
        return Response({
            'success': True,
            'order_id': data.get('id'),
            'links': data.get('links', [])
        })
        
    except requests.exceptions.RequestException as e:
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        log_api_request(
            endpoint='/api/paypal/create-order/',
            method='POST',
            request_data={'amount': amount, 'currency': currency},
            response_data={'error': str(e)},
            status_code=400,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            duration=duration
        )
        
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def capture_paypal_order(request, order_id):
    """
    Capture PayPal order
    """
    start_time = datetime.now()
    
    auth = base64.b64encode(f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_SECRET}".encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/json'
    }
    
    capture_url = f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture"
    
    try:
        response = requests.post(capture_url, headers=headers, json={}, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        log_api_request(
            endpoint=f'/api/paypal/capture-order/{order_id}/',
            method='POST',
            request_data={'order_id': order_id},
            response_data=data,
            status_code=200,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            duration=duration
        )
        
        return Response({
            'success': True,
            'status': data.get('status'),
            'payment_id': data.get('id')
        })
        
    except requests.exceptions.RequestException as e:
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        log_api_request(
            endpoint=f'/api/paypal/capture-order/{order_id}/',
            method='POST',
            request_data={'order_id': order_id},
            response_data={'error': str(e)},
            status_code=400,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            duration=duration
        )
        
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_stripe_payment_intent(request):
    """
    Create Stripe payment intent
    """
    start_time = datetime.now()
    
    amount = request.data.get('amount')
    currency = request.data.get('currency', 'kes')
    metadata = request.data.get('metadata', {})
    
    try:
        # Convert amount to cents
        amount_cents = int(float(amount) * 100)
        
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            metadata=metadata,
            automatic_payment_methods={
                'enabled': True,
            },
        )
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        log_api_request(
            endpoint='/api/stripe/create-payment-intent/',
            method='POST',
            request_data={'amount': amount, 'currency': currency, 'metadata': metadata},
            response_data={'client_secret': intent.client_secret, 'id': intent.id},
            status_code=200,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            duration=duration
        )
        
        return Response({
            'success': True,
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id,
            'amount': intent.amount,
            'currency': intent.currency
        })
        
    except stripe.error.StripeError as e:
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        log_api_request(
            endpoint='/api/stripe/create-payment-intent/',
            method='POST',
            request_data={'amount': amount, 'currency': currency, 'metadata': metadata},
            response_data={'error': str(e)},
            status_code=400,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            duration=duration
        )
        
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_webhook(request):
    """
    Handle Stripe webhook
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        # Handle different event types
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            # Update donation status
            try:
                donation = Donation.objects.get(transaction_id=payment_intent['id'])
                donation.status = 'completed'
                donation.save()
            except Donation.DoesNotExist:
                pass
                
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            # Update donation status to failed
            try:
                donation = Donation.objects.get(transaction_id=payment_intent['id'])
                donation.status = 'failed'
                donation.save()
            except Donation.DoesNotExist:
                pass
        
        log_api_request(
            endpoint='/api/stripe/webhook/',
            method='POST',
            request_data={'event_type': event['type']},
            response_data={'received': True},
            status_code=200,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            duration=0
        )
        
        return Response({'status': 'success'})
        
    except stripe.error.SignatureVerificationError as e:
        return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def donation_stats(request):
    """
    Get donation statistics
    """
    from django.db.models import Count, Sum, Avg
    from datetime import datetime, timedelta
    
    # Get filters
    days = int(request.GET.get('days', 30))
    start_date = datetime.now() - timedelta(days=days)
    
    # Get donation statistics
    donations = Donation.objects.filter(created_at__gte=start_date, status='completed')
    
    stats = {
        'total_donations': donations.count(),
        'total_amount': donations.aggregate(Sum('amount'))['amount__sum'] or 0,
        'average_donation': donations.aggregate(Avg('amount'))['amount__avg'] or 0,
        'by_method': list(donations.values('payment_method').annotate(
            count=Count('id'),
            total=Sum('amount')
        )),
        'daily_totals': []
    }
    
    # Get daily totals
    for i in range(days):
        date = start_date + timedelta(days=i)
        day_total = donations.filter(created_at__date=date.date()).aggregate(
            total=Sum('amount')
        )['total'] or 0
        stats['daily_totals'].append({
            'date': date.strftime('%Y-%m-%d'),
            'amount': float(day_total)
        })
    
    return Response(stats)

@api_view(['GET'])
@permission_classes([AllowAny])
def program_list(request):
    """
    Get program list
    """
    from programs.models import Program
    from .serializers import ProgramSerializer

    programs = Program.objects.filter(is_active=True)
    serializer = ProgramSerializer(programs, many=True)

    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def event_list(request):
    """
    Get event list
    """
    # No Event model exists, return empty list
    return Response([])

@api_view(['POST'])
@permission_classes([AllowAny])
def paypal_success(request):
    """
    PayPal success callback
    """
    order_id = request.data.get('orderID')
    payment_id = request.data.get('paymentID')
    
    return Response({
        'success': True,
        'order_id': order_id,
        'payment_id': payment_id
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def paypal_cancel(request):
    """
    PayPal cancel callback
    """
    return Response({
        'success': False,
        'message': 'Payment cancelled'
    })