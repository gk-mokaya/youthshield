from django.core.management.base import BaseCommand
from django.db import models
from donations.models import Donation

class Command(BaseCommand):
    help = 'Populate receipt numbers for existing donations'

    def handle(self, *args, **options):
        donations = Donation.objects.filter(receipt_number__isnull=True).order_by('created_at')
        count = 0
        for donation in donations:
            max_receipt = Donation.objects.aggregate(models.Max('receipt_number'))['receipt_number__max']
            donation.receipt_number = (max_receipt or 0) + 1
            donation.save()
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully populated receipt numbers for {count} donations'))
