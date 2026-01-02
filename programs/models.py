from django.db import models

class Program(models.Model):
    PROGRAM_CATEGORIES = (
        ('education', 'Education & Awareness'),
        ('mentorship', 'Mentorship'),
        ('rehabilitation', 'Rehabilitation'),
        ('career', 'Career Building'),
        ('women', 'Women Empowerment'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=PROGRAM_CATEGORIES)
    image = models.ImageField(upload_to='programs/')
    objectives = models.TextField(help_text="List program objectives")
    target_audience = models.TextField()
    duration = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['title']
    
    def get_objectives_list(self):
        """Return first 3 objectives as a list"""
        return [obj.strip() for obj in self.objectives.split('\n')[:3] if obj.strip()]

    def __str__(self):
        return self.title

class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon_class = models.CharField(max_length=50)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class Objective(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon_class = models.CharField(max_length=50)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title