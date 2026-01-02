import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youthshield.settings')
django.setup()

from django.utils import timezone

print("Current timezone:", settings.TIME_ZONE)
print("Current date/time:", timezone.now())
print("Current date:", timezone.now().date())
print("Current time:", timezone.now().time())
