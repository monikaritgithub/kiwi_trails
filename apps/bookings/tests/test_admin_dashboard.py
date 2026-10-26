"""Tests for the administrator dashboard summary.
Checks permissions, booking totals, departure dates, and empty results.
"""

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.bookings.models import Booking
from apps.catalog.models import Category, Tour
from apps.core.testing import make_admin, make_client, make_customer
from apps.departures.models import Departure


class AdminDashboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = make_admin()
        cls.customer = make_customer(
            email="dashboard-customer@example.test",
            full_name="Aroha Smith",
        )
        cls.now = timezone.now()
        cls.category = Category.objects.create(name="Dashboard tours")
        cls.tour = cls.make_tour("Active tour", "active")
        cls.archived_tour = cls.make_tour("Archived tour", "archived")
        cls.departure = cls.make_departure(
            cls.now + timedelta(days=30),
            "scheduled",
        )

        cls.bookings = {}
        amounts = {
            "pending": "900.00",
            "approved": "120.25",
            "rejected": "800.00",
            "cancelled": "700.00",
            "completed": "230.50",
        }
        for index, (status, amount) in enumerate(amounts.items()):
            cls.bookings[status] = cls.make_booking(
                f"KT-DASH{index}",
                status,
                amount,
            )

    @classmethod
    def make_tour(cls, title, status):
        return Tour.objects.create(
            title=title,
            description="A scenic tour.",
            location="Taupo",
            category=cls.category,
            price_per_person=Decimal("200.00"),
            duration_days=1,
            itinerary="Meet at the lake.",
            status=status,
        )

    @classmethod
    def make_departure(cls, start_datetime, status, tour=None):
        return Departure.objects.create(
            tour=tour or cls.tour,
            start_datetime=start_datetime,
            booking_deadline=start_datetime - timedelta(days=1),
            capacity=100,
            status=status,
        )

    @classmethod
    def make_booking(cls, reference, status, total_price):
        total = Decimal(total_price)
        subtotal = total + Decimal("10.00")
        return Booking.objects.create(
            booking_reference=reference,
            user=cls.customer,
            departure=cls.departure,
            traveller_count=2,
            price_per_person=subtotal / 2,
            subtotal=subtotal,
            discount_amount=Decimal("10.00"),
            total_price=total,
            status=status,
        )

    def setUp(self):
        self.client = make_client(self.admin)
        self.url = reverse("admin-dashboard")

    def get_summary(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        self.assertTrue(payload["success"])
        return payload["data"]

    def assert_error(self, response, status_code, code):
        self.assertEqual(response.status_code, status_code, response.content)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], code)

    def test_admin_receives_documented_summary(self):
        data = self.get_summary()

        self.assertEqual(
            data,
            {
                "active_tours": 1,
                "upcoming_departures": 1,
                "bookings_by_status": {
                    "pending": 1,
                    "approved": 1,
                    "rejected": 1,
                    "cancelled": 1,
                    "completed": 1,
                },
                "total_value": 350.75,
            },
        )

    def test_customer_is_forbidden(self):
        self.client = make_client(self.customer)

        response = self.client.get(self.url)

        self.assert_error(response, 403, "FORBIDDEN")

    def test_anonymous_request_is_unauthenticated(self):
        self.client = APIClient()

        response = self.client.get(self.url)

        self.assert_error(response, 401, "UNAUTHENTICATED")

    def test_only_active_tours_are_counted(self):
        self.make_tour("Another active tour", "active")
        self.make_tour("Another archived tour", "archived")

        self.assertEqual(self.get_summary()["active_tours"], 2)

    def test_only_future_scheduled_departures_are_counted(self):
        self.make_departure(self.now + timedelta(days=10), "scheduled")
        self.make_departure(self.now - timedelta(days=10), "scheduled")
        self.make_departure(self.now + timedelta(days=10), "cancelled")
        self.make_departure(self.now + timedelta(days=10), "completed")

        with patch("apps.bookings.services.timezone") as clock:
            clock.now.return_value = self.now
            data = self.get_summary()

        self.assertEqual(data["upcoming_departures"], 2)

    def test_departure_starting_exactly_now_is_not_upcoming(self):
        Departure.objects.filter(pk=self.departure.pk).update(
            start_datetime=self.now,
        )

        with patch("apps.bookings.services.timezone") as clock:
            clock.now.return_value = self.now
            data = self.get_summary()

        self.assertEqual(data["upcoming_departures"], 0)

    def test_scheduled_departure_on_archived_tour_is_counted(self):
        self.make_departure(
            self.now + timedelta(days=10),
            "scheduled",
            tour=self.archived_tour,
        )

        self.assertEqual(self.get_summary()["upcoming_departures"], 2)

    def test_status_counts_count_bookings_not_travellers(self):
        self.make_booking("KT-DASH-EXTRA", "approved", "50.00")
        Booking.objects.filter(status="approved").update(traveller_count=5)

        data = self.get_summary()

        self.assertEqual(data["bookings_by_status"]["approved"], 2)
        self.assertEqual(sum(data["bookings_by_status"].values()), 6)

    def test_missing_statuses_are_returned_as_zero(self):
        Booking.objects.exclude(status="approved").delete()

        data = self.get_summary()

        self.assertEqual(
            data["bookings_by_status"],
            {
                "pending": 0,
                "approved": 1,
                "rejected": 0,
                "cancelled": 0,
                "completed": 0,
            },
        )

    def test_total_value_includes_only_approved_and_completed(self):
        self.make_booking("KT-DASH-APPROVED", "approved", "10.10")
        self.make_booking("KT-DASH-COMPLETED", "completed", "20.20")
        self.make_booking("KT-DASH-PENDING", "pending", "999.00")

        data = self.get_summary()

        self.assertEqual(Decimal(str(data["total_value"])), Decimal("381.05"))

    def test_total_value_uses_saved_prices_after_discount(self):
        Tour.objects.filter(pk=self.tour.pk).update(
            price_per_person=Decimal("9999.00"),
        )

        data = self.get_summary()

        self.assertEqual(Decimal(str(data["total_value"])), Decimal("350.75"))

    def test_total_value_is_zero_without_eligible_bookings(self):
        Booking.objects.filter(
            status__in=["approved", "completed"],
        ).delete()

        data = self.get_summary()

        self.assertEqual(data["total_value"], 0)
        self.assertEqual(data["bookings_by_status"]["pending"], 1)

    def test_no_bookings_returns_all_statuses_and_zero_value(self):
        Booking.objects.all().delete()

        data = self.get_summary()

        self.assertEqual(
            data["bookings_by_status"],
            {
                "pending": 0,
                "approved": 0,
                "rejected": 0,
                "cancelled": 0,
                "completed": 0,
            },
        )
        self.assertEqual(data["total_value"], 0)
        self.assertEqual(data["active_tours"], 1)

    def test_empty_database_returns_zero_metrics(self):
        Booking.objects.all().delete()
        Departure.objects.all().delete()
        Tour.objects.all().delete()

        data = self.get_summary()

        self.assertEqual(data["active_tours"], 0)
        self.assertEqual(data["upcoming_departures"], 0)
        self.assertEqual(data["total_value"], 0)
        self.assertEqual(
            data["bookings_by_status"],
            {
                "pending": 0,
                "approved": 0,
                "rejected": 0,
                "cancelled": 0,
                "completed": 0,
            },
        )

    def test_bookings_from_multiple_customers_are_counted(self):
        other_customer = make_customer(
            email="other-dashboard@example.test",
            full_name="Tane Ngata",
        )
        booking = self.make_booking("KT-DASH-OTHER", "approved", "40.00")
        booking.user = other_customer
        booking.save(update_fields=["user"])

        data = self.get_summary()

        self.assertEqual(data["bookings_by_status"]["approved"], 2)
        self.assertEqual(Decimal(str(data["total_value"])), Decimal("390.75"))

    def test_get_does_not_modify_database_records(self):
        bookings_before = list(Booking.objects.order_by("id").values())
        departures_before = list(Departure.objects.order_by("id").values())
        tours_before = list(Tour.objects.order_by("id").values())

        self.get_summary()

        self.assertEqual(
            list(Booking.objects.order_by("id").values()),
            bookings_before,
        )
        self.assertEqual(
            list(Departure.objects.order_by("id").values()),
            departures_before,
        )
        self.assertEqual(
            list(Tour.objects.order_by("id").values()),
            tours_before,
        )
