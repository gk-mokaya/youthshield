from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('user', 'Regular User'),
        ('staff', 'Staff Member'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='User')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Make email unique and required
    email = models.EmailField(unique=True, blank=False)

    # Add related_name to avoid clashes with built-in User model
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='customuser_set',  # Changed from default
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',  # Changed from default
        related_query_name='customuser',
    )

    def __str__(self):
        return f"{self.username} - {self.get_user_type_display()}"

    def is_staff_member(self):
        return self.user_type == 'staff'

    class Meta:
        db_table = 'custom_user'

    # Override the USERNAME_FIELD to use email for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
