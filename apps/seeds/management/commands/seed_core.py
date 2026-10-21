"""Management command to seed core models.
Creates baseline users catalog departures and coupons.
Provides empty implementation during initial setup.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        pass
