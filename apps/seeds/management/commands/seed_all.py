"""Management command to execute all seed routines.
Runs seed core seed bookings and seed reviews in sequential order.
Orchestrates sample data population across the platform.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Run all seed commands in sequence"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Reset seed data before running",
        )

    def handle(self, *args, **options):
        reset = options.get("reset", False)
        kwargs = {"reset": True} if reset else {}

        self.stdout.write("Running seed_core...")
        call_command("seed_core", **kwargs)

        try:
            self.stdout.write("Running seed_bookings...")
            call_command("seed_bookings", **kwargs)
        except (CommandError, TypeError):
            self.stdout.write("seed_bookings command not available yet; skipping.")

        try:
            self.stdout.write("Running seed_reviews...")
            call_command("seed_reviews", **kwargs)
        except CommandError:
            self.stdout.write("seed_reviews command not available yet; skipping.")
