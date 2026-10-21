"""Seed command populating customer reviews on completed bookings.
Creates three ratings and comments while leaving one booking unreviewed.
Safe to rerun multiple times and supports reset option.
"""

from django.core.management.base import BaseCommand

from apps.bookings.models import Booking
from apps.reviews.models import Review


class Command(BaseCommand):
    help = "Seed reviews on completed tour bookings"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing reviews before populating",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            Review.objects.all().delete()

        completed_bookings = list(
            Booking.objects.filter(status="completed")
            .select_related("user", "departure__tour")
            .order_by("id")
        )
        if len(completed_bookings) < 3:
            self.stdout.write(
                self.style.WARNING(
                    "Fewer than three completed bookings found; skipping seed reviews."
                )
            )
            return

        review_configs = [
            (5, "Unforgettable experience, breathtaking views and outstanding guide."),
            (4, "Very well organized and friendly guide throughout the journey."),
            (3, ""),
        ]

        count = 0
        for booking, (rating, comment) in zip(completed_bookings[:3], review_configs, strict=False):
            Review.objects.update_or_create(
                booking=booking,
                defaults={
                    "user": booking.user,
                    "tour": booking.departure.tour,
                    "rating": rating,
                    "comment": comment,
                },
            )
            count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully seeded {count} reviews on completed bookings.")
        )
