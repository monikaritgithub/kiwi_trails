"""Management command to seed booking and attendance records.
Creates sample customer bookings and attendance status rows.
Provides empty implementation during initial setup.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        pass
