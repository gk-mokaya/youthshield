from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import JSONField

class BackupJob(models.Model):
    FREQUENCY_CHOICES = [
        ('disabled', 'Disabled'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    CRITERIA_CHOICES = [
        ('time', 'Time-based'),
        ('size', 'Database Size Change'),
        ('activity', 'User Activity'),
        ('manual', 'Manual Trigger'),
    ]

    name = models.CharField(max_length=100, unique=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='disabled')
    backup_time = models.TimeField(default='02:00')
    criteria = models.CharField(max_length=20, choices=CRITERIA_CHOICES, default='time')
    size_threshold = models.PositiveIntegerField(
        help_text='Size threshold in MB for size-based backups',
        default=100
    )
    activity_threshold = models.PositiveIntegerField(
        help_text='Number of new records for activity-based backups',
        default=100
    )
    max_backups = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.frequency})"

    def save(self, *args, **kwargs):
        if self.frequency != 'disabled':
            self.calculate_next_run()
        super().save(*args, **kwargs)

    def calculate_next_run(self):
        """Calculate the next run time based on frequency"""
        now = timezone.now()

        # Ensure backup_time is a Time object
        if isinstance(self.backup_time, str):
            from datetime import datetime
            self.backup_time = datetime.strptime(self.backup_time, '%H:%M').time()

        if self.frequency == 'daily':
            next_run = now.replace(hour=self.backup_time.hour, minute=self.backup_time.minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        elif self.frequency == 'weekly':
            # Run on Monday at backup_time
            days_ahead = (7 - now.weekday()) % 7
            if days_ahead == 0 and (now.hour > self.backup_time.hour or
                                   (now.hour == self.backup_time.hour and now.minute >= self.backup_time.minute)):
                days_ahead = 7
            next_run = (now + timedelta(days=days_ahead)).replace(
                hour=self.backup_time.hour, minute=self.backup_time.minute, second=0, microsecond=0
            )
        elif self.frequency == 'monthly':
            # Run on the 1st of next month at backup_time
            if now.month == 12:
                next_month = now.replace(year=now.year + 1, month=1, day=1)
            else:
                next_month = now.replace(month=now.month + 1, day=1)

            next_run = next_month.replace(hour=self.backup_time.hour, minute=self.backup_time.minute, second=0, microsecond=0)
            if next_run <= now:
                # If we're past the backup time this month, schedule for next month
                if next_run.month == 12:
                    next_run = next_run.replace(year=next_run.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=next_run.month + 1)
        else:
            self.next_run = None
            return

        self.next_run = next_run

    def should_run_backup(self):
        """Check if backup should run based on criteria"""
        if not self.is_active or self.frequency == 'disabled':
            return False

        now = timezone.now()

        # Time-based check
        if self.criteria == 'time':
            return self.next_run and now >= self.next_run

        # Size-based check
        elif self.criteria == 'size':
            from django.db import connection
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT pg_database_size(current_database())")
                    db_size_bytes = cursor.fetchone()[0]
                    db_size_mb = db_size_bytes / (1024 * 1024)

                    # Check if size has increased significantly since last backup
                    if self.last_run:
                        # For simplicity, we'll check if current size > threshold
                        # In a real implementation, you might track size changes
                        return db_size_mb > self.size_threshold
                    else:
                        # First backup
                        return True
            except:
                # Fallback for non-PostgreSQL databases
                return False

        # Activity-based check
        elif self.criteria == 'activity':
            # Check for new records since last backup
            from users.models import CustomUser
            from donations.models import Donation
            from programs.models import Program
            from testimonials.models import Testimonial
            from core.models import ContactMessage

            since_time = self.last_run if self.last_run else now - timedelta(days=1)

            new_users = CustomUser.objects.filter(date_joined__gte=since_time).count()
            new_donations = Donation.objects.filter(created_at__gte=since_time).count()
            new_programs = Program.objects.filter(created_at__gte=since_time).count()
            new_testimonials = Testimonial.objects.filter(created_at__gte=since_time).count()
            new_messages = ContactMessage.objects.filter(created_at__gte=since_time).count()

            total_activity = new_users + new_donations + new_programs + new_testimonials + new_messages
            return total_activity >= self.activity_threshold

        return False

class BackupLog(models.Model):
    ACTION_CHOICES = [
        ('created', 'Backup Created'),
        ('deleted', 'Backup Deleted'),
        ('downloaded', 'Backup Downloaded'),
        ('failed', 'Backup Failed'),
        ('scheduled', 'Backup Scheduled'),
    ]

    job = models.ForeignKey(BackupJob, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    message = models.TextField()
    backup_file = models.CharField(max_length=255, null=True, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    success = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        ordering = ['-created_at']

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('view', 'Page View'),
        ('create', 'Create Record'),
        ('update', 'Update Record'),
        ('delete', 'Delete Record'),
        ('export', 'Export Data'),
        ('import', 'Import Data'),
        ('backup', 'Backup Operation'),
        ('settings', 'Settings Change'),
        ('other', 'Other Action'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='other')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    url = models.CharField(max_length=500, blank=True)
    method = models.CharField(max_length=10, blank=True)
    details = JSONField(null=True, blank=True, help_text='Additional details about the action')
    model_name = models.CharField(max_length=100, blank=True, help_text='Name of the model affected by the action')
    object_id = models.CharField(max_length=100, blank=True, help_text='ID of the object affected by the action')
    message = models.TextField(blank=True, help_text='Description of the action performed')
    timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True, help_text='User agent string from browser')

    def __str__(self):
        user_name = self.user.username if self.user else 'Anonymous'
        return f"{user_name} - {self.action} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['ip_address']),
        ]
