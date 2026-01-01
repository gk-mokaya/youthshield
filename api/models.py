from django.db import models
from django.conf import settings

class APILog(models.Model):
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10)
    request_data = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict)
    status_code = models.IntegerField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField(help_text="Request duration in milliseconds")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"

class APIKey(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    key = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"