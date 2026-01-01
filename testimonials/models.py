from django.db import models
from users.models import CustomUser
import django.utils.timezone as timezone

class Testimonial(models.Model):
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    position = models.CharField(max_length=100, blank=True, null=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_testimonials')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                name='one_testimonial_per_user'
            )
    ]
    def __str__(self):
        return f"Testimonial by {self.user.username} - {self.get_rating_display()}"