
from django import forms
from django.core.exceptions import ValidationError
from .models import Donation

class DonationForm(forms.ModelForm):

    class Meta:
        model = Donation
        fields = ['amount', 'currency', 'payment_method', 'donor_name',
                 'donor_email', 'donor_phone', 'is_anonymous', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': 1, 'step': 'any', 'placeholder': 'Enter amount', 'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-control'}),
            'payment_method': forms.RadioSelect(),
            'donor_name': forms.TextInput(attrs={'placeholder': 'Your name', 'class': 'form-control'}),
            'donor_email': forms.EmailInput(attrs={'placeholder': 'Your email', 'class': 'form-control'}),
            'donor_phone': forms.TextInput(attrs={'placeholder': 'Phone number for M-Pesa (e.g., 254712345678)', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional message', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set currency choices to all currencies
        self.fields['currency'].choices = Donation.CURRENCY_CHOICES

        # Set default payment method if not provided
        if not self.data and not self.instance.pk:
            self.fields['payment_method'].initial = 'mpesa'

        # Make phone optional for all payment methods
        self.fields['donor_phone'].required = False

        # Set currency behavior based on payment method
        payment_method = self.data.get('payment_method') if self.data else getattr(self.instance, 'payment_method', 'mpesa')
        if payment_method == 'mpesa':
            self.fields['currency'].initial = 'KES'
            self.fields['currency'].widget.attrs['disabled'] = 'disabled'
            # Ensure currency is set to KES for M-Pesa even if not in POST data
            if self.data and 'currency' not in self.data:
                self.data = self.data.copy()
                self.data['currency'] = 'KES'
        else:
            if 'disabled' in self.fields['currency'].widget.attrs:
                del self.fields['currency'].widget.attrs['disabled']

    def clean_donor_phone(self):
        """Validate and format phone number for M-Pesa"""
        phone = self.cleaned_data.get('donor_phone')
        payment_method = self.cleaned_data.get('payment_method')

        if payment_method == 'mpesa':
            if not phone:
                raise ValidationError('Phone number is required for M-Pesa payments.')
            # Remove any spaces, hyphens, or other non-digit characters
            phone = ''.join(filter(str.isdigit, phone))

            # Check if it's a Kenyan number
            if phone.startswith('0') and len(phone) == 10:
                # Convert 07XXXXXXXX to 2547XXXXXXXX
                phone = '254' + phone[1:]
            elif phone.startswith('7') and len(phone) == 9:
                # Convert 7XXXXXXXX to 2547XXXXXXXX
                phone = '254' + phone
            elif phone.startswith('254') and len(phone) == 12:
                # Already in correct format
                pass
            else:
                raise ValidationError('Please enter a valid Kenyan phone number (e.g., 0712345678 or 254712345678)')

            # Final validation
            if not (phone.startswith('254') and len(phone) == 12):
                raise ValidationError('Phone number must be in format 254XXXXXXXXX')

        return phone

    def clean_currency(self):
        """Ensure currency is set correctly based on payment method"""
        currency = self.cleaned_data.get('currency')
        payment_method = self.cleaned_data.get('payment_method')

        if payment_method == 'mpesa':
            return 'KES'

        # For non-mpesa payments, validate that currency is selected and valid
        if not currency:
            raise ValidationError('Please select a currency for your donation.')

        # Check if selected currency is in the allowed list
        valid_currencies = [code for code, name in Donation.CURRENCY_CHOICES]
        if currency not in valid_currencies:
            raise ValidationError('Please select a valid currency.')

        return currency
