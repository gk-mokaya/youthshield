from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from staff_dashboard.models import BackupJob, BackupLog
import os
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run scheduled database backups based on BackupJob settings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force run backups regardless of schedule',
        )
        parser.add_argument(
            '--job-name',
            type=str,
            help='Run backup for specific job name only',
        )

    def handle(self, *args, **options):
        self.stdout.write('Checking for scheduled backups...')

        # Get backup jobs to process
        if options['job_name']:
            try:
                backup_jobs = [BackupJob.objects.get(name=options['job_name'], is_active=True)]
            except BackupJob.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Job "{options["job_name"]}" not found or not active.')
                )
                return
        else:
            backup_jobs = BackupJob.objects.filter(is_active=True).exclude(frequency='disabled')

        if not backup_jobs:
            self.stdout.write('No active backup jobs found.')
            return

        for job in backup_jobs:
            try:
                should_run = options['force'] or job.should_run_backup()

                if should_run:
                    self.stdout.write(f'Running backup for job: {job.name}')
                    success, message, backup_file, file_size = self.create_backup(job)

                    if success:
                        # Update job's last run time and calculate next run
                        job.last_run = timezone.now()
                        job.calculate_next_run()
                        job.save()

                        self.stdout.write(
                            self.style.SUCCESS(f'Successfully created backup: {backup_file}')
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'Failed to create backup for {job.name}: {message}')
                        )

                    # Log the backup attempt
                    BackupLog.objects.create(
                        job=job,
                        action='created' if success else 'failed',
                        message=message,
                        backup_file=backup_file,
                        file_size=file_size,
                        success=success
                    )

                else:
                    self.stdout.write(f'Skipping job {job.name} - not scheduled to run yet')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing job {job.name}: {str(e)}')
                )
                BackupLog.objects.create(
                    job=job,
                    action='failed',
                    message=f'Unexpected error: {str(e)}',
                    success=False
                )

        # Clean up old backups
        self.cleanup_old_backups()

    def create_backup(self, job):
        """Create a database backup"""
        try:
            # Create backups directory if it doesn't exist
            backup_dir = os.path.join(settings.BASE_DIR, 'backups')
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            # Generate backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{job.name.lower().replace(' ', '_')}_{timestamp}.bak"
            backup_path = os.path.join(backup_dir, backup_name)

            # Get database path
            db_path = str(settings.DATABASES['default']['NAME'])

            # Create SQLite backup
            conn = sqlite3.connect(db_path)
            backup_conn = sqlite3.connect(backup_path)

            with backup_conn:
                conn.backup(backup_conn)

            conn.close()
            backup_conn.close()

            # Get file size
            file_size = os.path.getsize(backup_path)

            return True, f'Backup created successfully: {backup_name}', backup_name, file_size

        except Exception as e:
            return False, f'Failed to create backup: {str(e)}', None, None

    def cleanup_old_backups(self):
        """Clean up old backups based on max_backups setting"""
        try:
            backup_dir = os.path.join(settings.BASE_DIR, 'backups')
            if not os.path.exists(backup_dir):
                return

            # Get all backup files
            backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.bak')]

            if not backup_files:
                return

            # Sort by creation time (newest first)
            backup_files.sort(key=lambda x: os.path.getctime(os.path.join(backup_dir, x)), reverse=True)

            # Get the maximum backups from all jobs
            max_backups = max([job.max_backups for job in BackupJob.objects.all()] + [10])

            # Delete old backups
            for old_file in backup_files[max_backups:]:
                file_path = os.path.join(backup_dir, old_file)
                try:
                    os.remove(file_path)
                    BackupLog.objects.create(
                        action='deleted',
                        message=f'Old backup deleted: {old_file}',
                        success=True
                    )
                    self.stdout.write(f'Deleted old backup: {old_file}')
                except OSError as e:
                    self.stdout.write(
                        self.style.WARNING(f'Failed to delete old backup {old_file}: {str(e)}')
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during cleanup: {str(e)}')
            )
