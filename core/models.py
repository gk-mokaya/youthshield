from django.db import models

class WebsiteSetting(models.Model):
    name = models.CharField(max_length=100)
    Registration_Number = models.CharField(max_length=100, unique=True,default="S/NO 1234/5678/90")
    logo = models.ImageField(upload_to='logos/')
    primary_color = models.CharField(max_length=7, default='#2c3e50')
    secondary_color = models.CharField(max_length=7, default='#3498db')
    accent_color = models.CharField(max_length=7, default='#e74c3c')
    mission = models.TextField()
    vision = models.TextField()
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    address = models.TextField()

    # Social Media Links
    facebook_url = models.URLField(blank=True, null=True, help_text="Facebook page URL")
    twitter_url = models.URLField(blank=True, null=True, help_text="Twitter/X profile URL")
    instagram_url = models.URLField(blank=True, null=True, help_text="Instagram profile URL")
    linkedin_url = models.URLField(blank=True, null=True, help_text="LinkedIn page URL")
    tiktok_url = models.URLField(blank=True, null=True, help_text="TikTok profile URL")
    whatsapp_channel_url = models.URLField(blank=True, null=True, help_text="WhatsApp channel URL")

    # Additional Contact Information
    website_url = models.URLField(blank=True, null=True, help_text="Official website URL")
    emergency_phone = models.CharField(max_length=20, blank=True, null=True, help_text="Emergency contact number")
    support_email = models.EmailField(blank=True, null=True, help_text="Support email address")

    # Organization Details
    tagline = models.CharField(max_length=200, blank=True, null=True, help_text="Short tagline or slogan")
    copyright_text = models.CharField(max_length=200, default="© 2025 Youth Shield Foundation. All rights reserved.", help_text="Copyright notice")
    description = models.TextField(blank=True, null=True, help_text="Brief organization description")

    def __str__(self):
        return self.name

class CoreValue(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon_class = models.CharField(max_length=50)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)  # Add this field

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

class BoardMember(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    bio = models.TextField()
    photo = models.ImageField(upload_to='board/')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)  # Add this field

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} - {self.position}"

class ExecutiveCommittee(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='executive/', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.name} - {self.position}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name}: {self.subject}"
