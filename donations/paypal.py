import requests
import base64
from django.conf import settings

def get_paypal_access_token():
    """Get PayPal access token"""
    auth = base64.b64encode(f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_SECRET}".encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {'grant_type': 'client_credentials'}
    
    try:
        response = requests.post(
            'https://api-m.sandbox.paypal.com/v1/oauth2/token',
            headers=headers,
            data=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        print(f"PayPal Token Error: {e}")
        return None

def create_paypal_order(amount, currency='USD', return_url=None, cancel_url=None):
    """Create PayPal order"""
    access_token = get_paypal_access_token()
    if not access_token:
        return None
    
    headers = {
        'Authorization': f'Bearer {access_token}',
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
            "return_url": return_url or f"{settings.BASE_URL}/donations/paypal-success/",
            "cancel_url": cancel_url or f"{settings.BASE_URL}/donations/paypal-cancel/"
        }
    }
    
    try:
        response = requests.post(
            'https://api-m.sandbox.paypal.com/v2/checkout/orders',
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"PayPal Order Error: {e}")
        return None

def capture_paypal_order(order_id):
    """Capture PayPal payment"""
    access_token = get_paypal_access_token()
    if not access_token:
        return None
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f'https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture',
            headers=headers,
            json={},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"PayPal Capture Error: {e}")
        return None