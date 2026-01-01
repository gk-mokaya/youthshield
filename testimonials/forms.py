from django import forms
from .models import Testimonial

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ('content', 'rating','position')
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your experience with Youth Shield Foundation...'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Position (e.g., Student, Beneficiary)'
            }),
            'rating': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].widget.choices = [
            (5, '⭐⭐⭐⭐⭐ Excellent'),
            (4, '⭐⭐⭐⭐ Very Good'),
            (3, '⭐⭐⭐ Good'),
            (2, '⭐⭐ Fair'),
            (1, '⭐ Poor'),
        ]