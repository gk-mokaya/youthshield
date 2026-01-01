import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_payment_intent(amount, currency='kes', metadata=None):
    """Create Stripe payment intent"""
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency=currency,
            metadata=metadata or {}
        )
        return intent
    except stripe.error.StripeError as e:
        print(f"Stripe Error: {e}")
        return None

def create_stripe_customer(email, name=None):
    """Create Stripe customer"""
    try:
        customer = stripe.Customer.create(
            email=email,
            name=name
        )
        return customer
    except stripe.error.StripeError as e:
        print(f"Stripe Customer Error: {e}")
        return None

def handle_stripe_webhook(payload, sig_header):
    """Handle Stripe webhook"""
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )

        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            # Update donation status
            donation_id = payment_intent.get('metadata', {}).get('donation_id')
            if donation_id:
                from .models import Donation
                try:
                    donation = Donation.objects.get(id=donation_id)
                    donation.status = 'completed'
                    donation.save()
                    return True
                except Donation.DoesNotExist:
                    print(f"Donation {donation_id} not found")
                    return False
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            # Update donation status to failed
            donation_id = payment_intent.get('metadata', {}).get('donation_id')
            if donation_id:
                from .models import Donation
                try:
                    donation = Donation.objects.get(id=donation_id)
                    donation.status = 'failed'
                    donation.save()
                    return False
                except Donation.DoesNotExist:
                    print(f"Donation {donation_id} not found")
                    return False

        # For other events, just acknowledge receipt
        return None

    except stripe.error.SignatureVerificationError as e:
        print(f"Webhook signature verification failed: {e}")
        return False
    except Exception as e:
        print(f"Webhook error: {e}")
        return False
