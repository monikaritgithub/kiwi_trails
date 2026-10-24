"""Concurrent booking service tests.
Checks that competing customers cannot reserve the same last seat.
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal
from threading import Barrier
from time import sleep
from unittest.mock import patch

from django.db import close_old_connections, connections
from django.test import TransactionTestCase
from django.utils import timezone

from apps.bookings.models import Booking
from apps.bookings.services import calculate_booking_quote, create_booking
from apps.catalog.models import Category, Tour
from apps.core.exceptions import SeatsUnavailable
from apps.core.testing import make_customer
from apps.departures.models import Departure


class BookingConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.customers = [
            make_customer(email="first@kiwitrails.test"),
            make_customer(email="second@kiwitrails.test"),
        ]
        category = Category.objects.create(name="Scenic Tours")
        tour = Tour.objects.create(
            title="Last Seat Tour",
            description="A tour with one available seat.",
            location="Taupō",
            category=category,
            price_per_person=Decimal("150.00"),
            duration_days=1,
            itinerary="Meet the guide and explore the lake.",
        )
        self.departure = Departure.objects.create(
            tour=tour,
            start_datetime=timezone.now() + timedelta(days=30),
            booking_deadline=timezone.now() + timedelta(days=25),
            capacity=1,
        )

    def test_only_one_customer_can_book_the_last_seat(self):
        start = Barrier(2)

        def attempt_booking(customer):
            close_old_connections()
            try:
                start.wait(timeout=10)
                booking = create_booking(
                    user=customer,
                    departure_id=self.departure.id,
                    traveller_count=1,
                )
                return "created", booking.id
            except SeatsUnavailable:
                return "unavailable", None
            finally:
                connections.close_all()

        def slow_quote(*args, **kwargs):
            quote = calculate_booking_quote(*args, **kwargs)
            sleep(0.2)
            return quote

        with patch(
            "apps.bookings.services.calculate_booking_quote",
            side_effect=slow_quote,
        ):
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [
                    executor.submit(attempt_booking, customer) for customer in self.customers
                ]
                results = [future.result(timeout=15) for future in futures]

        outcomes = sorted(result[0] for result in results)
        self.assertEqual(outcomes, ["created", "unavailable"])
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(Booking.objects.get().traveller_count, 1)
        self.departure.refresh_from_db()
        self.assertEqual(self.departure.capacity, 1)
