import requests
import base64
import logging
import json
import time
from datetime import datetime
from django.conf import settings
from django.db import transaction, DatabaseError
from django.utils import timezone
from .models import Donation, MpesaTransaction

logger = logging.getLogger(__name__)

def get_mpesa_access_token():
    """Get M-Pesa access token"""
    if not settings.MPESA_CONSUMER_KEY or not settings.MPESA_CONSUMER_SECRET:
        logger.error("M-Pesa consumer key or secret not set")
        return None

    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate"
    auth = base64.b64encode(f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}".encode()).decode()

    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/json'
    }
    data = {'grant_type': 'client_credentials'}

    try:
        response = requests.get(auth_url, headers=headers, params=data, timeout=30)
        logger.info(f"Token response status: {response.status_code} - {response.text}")
        response.raise_for_status()
        response_data = response.json()
        access_token = response_data.get('access_token')
        if access_token:
            return access_token
        else:
            logger.error(f"Access token not found in response: {response_data}")
            return None
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON response: {response.text}")
        return None
    except Exception as e:
        logger.error(f"M-Pesa Token Error: {e}")
        return None

def generate_mpesa_password():
    """Generate M-Pesa password"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    return base64.b64encode(data.encode()).decode()

def initiate_stk_push(phone, amount, account_reference, description="Donation"):
    """Initiate STK Push"""
    access_token = get_mpesa_access_token()
    if not access_token:
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = generate_mpesa_password()
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": str(int(amount)),
        "PartyA": phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": "https://ysfdemo.pythonanywhere.com/donations/mpesa-callback/",
        "AccountReference": account_reference,
        "TransactionDesc": description
    }
    
    try:
        logger.info(f"STK Push payload: {payload}")
        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers=headers,
            timeout=30
        )
        logger.info(f"STK Push response status: {response.status_code} - {response.text}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"STK Push HTTP Error: {e} - Response: {response.text if 'response' in locals() else 'No response'}")
        return None
    except Exception as e:
        logger.error(f"STK Push Error: {e}")
        return None

def parse_mpesa_timestamp(timestamp_str):
    """Parse M-Pesa timestamp format (YYYYMMDDHHMMSS) to timezone-aware datetime object"""
    if not timestamp_str or not isinstance(timestamp_str, str):
        return None
    try:
        # M-Pesa format: YYYYMMDDHHMMSS
        naive_dt = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
        # Make it timezone-aware (assuming UTC)
        return timezone.make_aware(naive_dt, timezone=timezone.utc)
    except ValueError:
        logger.error(f"Invalid M-Pesa timestamp format: {timestamp_str}")
        return None

def handle_mpesa_callback(data):
    """Handle M-Pesa callback with retry logic for database locking"""
    max_retries = 3
    retry_delay = 0.5  # seconds

    for attempt in range(max_retries):
        try:
            with transaction.atomic():
                callback_data = data.get('Body', {}).get('stkCallback', {})
                result_code = callback_data.get('ResultCode')
                result_desc = callback_data.get('ResultDesc')
                checkout_id = callback_data.get('CheckoutRequestID')
                merchant_id = callback_data.get('MerchantRequestID')

                # Find donation by checkout ID
                try:
                    donation = Donation.objects.select_for_update().get(transaction_id=checkout_id)
                except Donation.DoesNotExist:
                    # Try to find by merchant ID
                    try:
                        donation = Donation.objects.select_for_update().get(transaction_id=merchant_id)
                    except Donation.DoesNotExist:
                        logger.error(f"Donation not found for checkout ID: {checkout_id}")
                        return False

                # Create or update MpesaTransaction record
                mpesa_transaction, created = MpesaTransaction.objects.get_or_create(
                    donation=donation,
                    defaults={
                        'checkout_request_id': checkout_id,
                        'merchant_request_id': merchant_id,
                        'result_code': result_code,
                        'result_desc': result_desc,
                        'raw_response': data
                    }
                )

                if result_code == 0:
                    # Success
                    donation.status = 'completed'
                    callback_metadata = callback_data.get('CallbackMetadata', {}).get('Item', [])

                    for item in callback_metadata:
                        if item.get('Name') == 'MpesaReceiptNumber':
                            mpesa_transaction.mpesa_receipt_number = item.get('Value')
                            # Update donation transaction_id with M-Pesa receipt number
                            donation.transaction_id = item.get('Value')
                        elif item.get('Name') == 'PhoneNumber':
                            mpesa_transaction.phone_number = item.get('Value')
                        elif item.get('Name') == 'TransactionDate':
                            mpesa_transaction.transaction_date = parse_mpesa_timestamp(item.get('Value'))

                    mpesa_transaction.save()
                    donation.save()
                    return True
                else:
                    # Failed
                    donation.status = 'failed'
                    donation.save()
                    return False

        except DatabaseError as e:
            if "unable to open database file" in str(e).lower() or "database is locked" in str(e).lower():
                if attempt < max_retries - 1:
                    logger.warning(f"Database locking error on attempt {attempt + 1}, retrying in {retry_delay}s: {e}")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    logger.error(f"Database locking error persisted after {max_retries} attempts: {e}")
                    return False
            else:
                logger.error(f"Database Error: {e}")
                return False
        except Exception as e:
            logger.error(f"Callback Error: {e}")
            return False

    return False
