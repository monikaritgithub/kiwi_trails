"""Management command to seed review records.
Creates sample customer ratings and comments on completed bookings.
Provides empty implementation during initial setup.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        pass
