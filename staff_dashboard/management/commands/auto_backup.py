from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create automatic database backup and clean up old backups'

    def add_arguments(self, parser):
        parser.add_argument(
            '--retention-days',
            type=int,
            default=30,
            help='Number of days to keep backups (default: 30)',
        )

    def handle(self, *args, **options):
        retention_days = options['retention_days']

        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            self.stdout.write(
                self.style.SUCCESS(f'Created backup directory: {backup_dir}')
            )

        # Create backup
        try:
            db_path = settings.DATABASES['default']['NAME']
            backup_name = f"auto_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            backup_path = os.path.join(backup_dir, backup_name)

            shutil.copy2(db_path, backup_path)
            self.stdout.write(
                self.style.SUCCESS(f'Backup created successfully: {backup_name}')
            )

            # Log the backup creation
            logger.info(f'Automatic backup created: {backup_name}')

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Failed to create backup: {str(e)}')
            )
            logger.error(f'Failed to create automatic backup: {str(e)}')
            return

        # Clean up old backups
        try:
            self.cleanup_old_backups(backup_dir, retention_days)
        except Exception as e:
            self.stderr.write(
                self.style.WARNING(f'Failed to cleanup old backups: {str(e)}')
            )
            logger.warning(f'Failed to cleanup old backups: {str(e)}')

    def cleanup_old_backups(self, backup_dir, retention_days):
        """Remove backups older than retention_days"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0

        for filename in os.listdir(backup_dir):
            if filename.endswith('.db'):
                file_path = os.path.join(backup_dir, filename)
                file_date = datetime.fromtimestamp(os.path.getctime(file_path))

                if file_date < cutoff_date:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f'Deleted old backup: {filename}')
                    except OSError as e:
                        self.stderr.write(
                            self.style.WARNING(f'Failed to delete {filename}: {str(e)}')
                        )

        if deleted_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Cleaned up {deleted_count} old backup(s)')
            )
