"""Management command to execute all seed routines.
Runs seed core seed bookings and seed reviews in sequential order.
Orchestrates sample data population across the platform.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command("seed_core")
        call_command("seed_bookings")
        call_command("seed_reviews")
