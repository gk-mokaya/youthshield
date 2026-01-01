from django.db import models
from django.conf import settings

class Donation(models.Model):
    PAYMENT_METHODS = (
        ('mpesa', 'M-Pesa'),
        ('paypal', 'PayPal'),
        ('card', 'Credit/Debit'),
        # ('bank', 'Bank Transfer'),  # Temporarily disabled
    )

    CURRENCY_CHOICES = (
        ('KES', 'Kenyan Shilling'),
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CAD', 'Canadian Dollar'),
        ('AUD', 'Australian Dollar'),
        ('CHF', 'Swiss Franc'),
        ('CNY', 'Chinese Yuan'),
        ('SEK', 'Swedish Krona'),
        ('NZD', 'New Zealand Dollar'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )

    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='KES')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='mpesa')
    transaction_id = models.CharField(max_length=100, unique=False)
    receipt_number = models.PositiveIntegerField(unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    donor_name = models.CharField(max_length=100)
    donor_email = models.EmailField()
    donor_phone = models.CharField(max_length=20, blank=True)
    is_anonymous = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.amount} {self.currency}"
    
    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Generate a transaction ID if not provided
        if not self.transaction_id:
            import uuid
            from datetime import datetime
            # Generate unique transaction ID
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_id = str(uuid.uuid4())[:8].upper()
            self.transaction_id = f"DON-{timestamp}-{unique_id}"

        # Ensure transaction_id is unique
        if Donation.objects.filter(transaction_id=self.transaction_id).exclude(pk=self.pk).exists():
            import uuid
            unique_part = str(uuid.uuid4())[:4].upper()
            self.transaction_id = f"{self.transaction_id}-{unique_part}"

        # Generate receipt number if not provided
        if self.receipt_number is None:
            max_receipt = Donation.objects.aggregate(models.Max('receipt_number'))['receipt_number__max']
            self.receipt_number = (max_receipt or 0) + 1

        super().save(*args, **kwargs)

class MpesaTransaction(models.Model):
    donation = models.OneToOneField(Donation, on_delete=models.CASCADE)
    checkout_request_id = models.CharField(max_length=100)
    merchant_request_id = models.CharField(max_length=100)
    result_code = models.IntegerField(null=True, blank=True)
    result_desc = models.CharField(max_length=255, blank=True)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=20)
    transaction_date = models.DateTimeField(null=True, blank=True)
    raw_response = models.JSONField(default=dict)
    
    def __str__(self):
        return self.checkout_request_id

class PayPalTransaction(models.Model):
    donation = models.OneToOneField(Donation, on_delete=models.CASCADE)
    paypal_order_id = models.CharField(max_length=100)
    paypal_payer_id = models.CharField(max_length=100, blank=True)
    capture_id = models.CharField(max_length=100, blank=True)
    raw_response = models.JSONField(default=dict)
    
    def __str__(self):
        return self.paypal_order_id

class CardTransaction(models.Model):
    donation = models.OneToOneField(Donation, on_delete=models.CASCADE)
    stripe_payment_intent_id = models.CharField(max_length=100)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    card_last4 = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=50, blank=True)
    raw_response = models.JSONField(default=dict)
    
    def __str__(self):
        return self.stripe_payment_intent_id