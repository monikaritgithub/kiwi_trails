"""Tests for customer booking history.
Checks ownership, ordering, filtering, pagination, and response fields.
"""

from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.bookings.models import Booking, BookingStatus
from apps.catalog.models import Category, Tour
from apps.core.testing import make_admin, make_client, make_customer
from apps.departures.models import Departure


class MyBookingsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = make_customer(email="history@kiwitrails.test")
        cls.other_customer = make_customer(email="other@kiwitrails.test")
        cls.admin = make_admin(email="history-admin@kiwitrails.test")

        category = Category.objects.create(name="History Tours")
        cls.tour = Tour.objects.create(
            title="Taupō Lake Cruise",
            description="A guided lake cruise.",
            location="Taupō",
            category=category,
            price_per_person=Decimal("150.00"),
            duration_days=1,
            itinerary="Meet at the lake and board the boat.",
            cancellation_days=7,
        )

        now = timezone.now()
        cls.departure = Departure.objects.create(
            tour=cls.tour,
            start_datetime=now + timedelta(days=30),
            booking_deadline=now + timedelta(days=25),
            capacity=100,
        )

    def setUp(self):
        self.client = make_client(self.customer)
        self.url = "/api/v1/bookings/my"

    def make_booking(self, user=None, status=BookingStatus.PENDING):
        number = Booking.objects.count() + 1
        return Booking.objects.create(
            booking_reference=f"KT-TEST{number:04d}",
            user=user if user is not None else self.customer,
            departure=self.departure,
            traveller_count=2,
            price_per_person=Decimal("150.00"),
            subtotal=Decimal("300.00"),
            discount_amount=Decimal("0.00"),
            total_price=Decimal("300.00"),
            status=status,
        )

    def test_empty_history(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"]["items"], [])
        self.assertEqual(payload["data"]["total"], 0)
        self.assertEqual(payload["data"]["page"], 1)
        self.assertEqual(payload["data"]["page_size"], 10)

    def test_only_returns_current_customers_bookings(self):
        own_booking = self.make_booking()
        self.make_booking(user=self.other_customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["total"], 1)
        self.assertEqual(
            [item["id"] for item in data["items"]],
            [own_booking.id],
        )

    def test_user_parameter_cannot_expose_another_customers_bookings(self):
        own_booking = self.make_booking()
        self.make_booking(user=self.other_customer)

        response = self.client.get(self.url, {"user": self.other_customer.id})

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["items"][0]["id"], own_booking.id)

    def test_returns_newest_bookings_first(self):
        older = self.make_booking()
        newer = self.make_booking()
        Booking.objects.filter(pk=older.pk).update(created_at=timezone.now() - timedelta(days=2))

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        items = response.json()["data"]["items"]
        self.assertEqual([item["id"] for item in items], [newer.id, older.id])

    def test_equal_timestamps_use_id_as_tiebreaker(self):
        first = self.make_booking()
        second = self.make_booking()
        Booking.objects.filter(pk__in=[first.pk, second.pk]).update(created_at=timezone.now())

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        items = response.json()["data"]["items"]
        self.assertEqual([item["id"] for item in items], [second.id, first.id])

    def test_filters_each_valid_status(self):
        for booking_status in BookingStatus.values:
            self.make_booking(status=booking_status)
            self.make_booking(user=self.other_customer, status=booking_status)

        for booking_status in BookingStatus.values:
            with self.subTest(status=booking_status):
                response = self.client.get(self.url, {"status": booking_status})

                self.assertEqual(response.status_code, 200)
                data = response.json()["data"]
                self.assertEqual(data["total"], 1)
                self.assertEqual(data["items"][0]["status"], booking_status)

    def test_invalid_status_is_rejected(self):
        response = self.client.get(self.url, {"status": "unknown"})

        self.assertEqual(response.status_code, 422)

    def test_pagination_returns_correct_page_and_total(self):
        bookings = [self.make_booking() for _ in range(3)]
        Booking.objects.filter(pk__in=[booking.pk for booking in bookings]).update(
            created_at=timezone.now()
        )

        response = self.client.get(self.url, {"page": 2, "page_size": 2})

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["page"], 2)
        self.assertEqual(data["page_size"], 2)
        self.assertEqual(data["total"], 3)
        self.assertEqual([item["id"] for item in data["items"]], [bookings[0].id])

    def test_invalid_pagination_is_rejected(self):
        self.make_booking()

        for params in [
            {"page": 0},
            {"page": "abc"},
            {"page_size": 0},
            {"page_size": "abc"},
            {"page": 999},
        ]:
            with self.subTest(params=params):
                response = self.client.get(self.url, params)

                self.assertEqual(response.status_code, 422)

    def test_returns_booking_details_and_original_price(self):
        booking = self.make_booking()
        Tour.objects.filter(pk=self.tour.pk).update(price_per_person=Decimal("200.00"))

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        item = response.json()["data"]["items"][0]
        self.assertEqual(item["id"], booking.id)
        self.assertEqual(item["booking_reference"], booking.booking_reference)
        self.assertEqual(item["traveller_count"], 2)
        self.assertEqual(item["price_per_person"], 150)
        self.assertEqual(item["subtotal"], 300)
        self.assertEqual(item["discount_amount"], 0)
        self.assertEqual(item["total_price"], 300)
        self.assertEqual(item["tour"]["id"], self.tour.id)
        self.assertEqual(item["tour"]["title"], "Taupō Lake Cruise")
        self.assertEqual(item["tour"]["location"], "Taupō")
        self.assertEqual(item["departure"]["id"], self.departure.id)
        self.assertIn("start_datetime", item["departure"])
        self.assertIsNone(item["coupon_code"])
        self.assertIsNone(item["pickup_preference"])
        self.assertIsNone(item["dietary_requirements"])
        self.assertIsNone(item["accessibility_needs"])
        self.assertIsNone(item["status_reason"])
        self.assertIsNone(item["cancelled_at"])
        self.assertIn("created_at", item)
        self.assertIn("updated_at", item)

    def test_cancellation_availability_depends_on_status(self):
        for booking_status in BookingStatus.values:
            self.make_booking(status=booking_status)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        items = response.json()["data"]["items"]
        for item in items:
            with self.subTest(status=item["status"]):
                expected = item["status"] in [
                    BookingStatus.PENDING,
                    BookingStatus.APPROVED,
                ]
                self.assertEqual(item["can_cancel"], expected)
                self.assertIsNotNone(item["cancel_deadline"])

    def test_cancellation_is_unavailable_after_deadline(self):
        self.make_booking()
        Departure.objects.filter(pk=self.departure.pk).update(
            start_datetime=timezone.now() + timedelta(days=2)
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        item = response.json()["data"]["items"][0]
        self.assertFalse(item["can_cancel"])

    def test_anonymous_user_cannot_access_history(self):
        response = APIClient().get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_admin_cannot_use_customer_history_endpoint(self):
        response = make_client(self.admin).get(self.url)

        self.assertEqual(response.status_code, 403)
