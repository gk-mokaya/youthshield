from django.contrib import admin
from .models import Donation, MpesaTransaction, PayPalTransaction, CardTransaction

class DonationAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'donor_name', 'amount', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'donor_name', 'donor_email']
    readonly_fields = ['created_at', 'updated_at']
    
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ['checkout_request_id', 'donation', 'phone_number', 'result_code', 'transaction_date']
    list_filter = ['result_code']
    search_fields = ['checkout_request_id', 'phone_number', 'mpesa_receipt_number']

admin.site.register(Donation, DonationAdmin)
admin.site.register(MpesaTransaction, MpesaTransactionAdmin)
admin.site.register(PayPalTransaction)
admin.site.register(CardTransaction)