"""Tests for individual booking details.
Checks owner and admin access, privacy, and missing bookings.
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


class BookingDetailTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = make_customer(email="detail@kiwitrails.test")
        cls.other_customer = make_customer(email="other-detail@kiwitrails.test")
        cls.admin = make_admin(email="detail-admin@kiwitrails.test")

        category = Category.objects.create(name="Detail Tours")
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
            capacity=10,
        )

        cls.booking = Booking.objects.create(
            booking_reference="KT-DETAIL01",
            user=cls.customer,
            departure=cls.departure,
            traveller_count=2,
            price_per_person=Decimal("150.00"),
            subtotal=Decimal("300.00"),
            discount_amount=Decimal("0.00"),
            total_price=Decimal("300.00"),
            status=BookingStatus.PENDING,
            pickup_preference="Hotel Grand",
            dietary_requirements="Vegetarian",
            accessibility_needs="Step-free access",
        )

    def setUp(self):
        self.client = make_client(self.customer)
        self.url = f"/api/v1/bookings/{self.booking.id}"

    def test_owner_can_view_full_booking_details(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])

        data = payload["data"]
        self.assertEqual(data["id"], self.booking.id)
        self.assertEqual(data["booking_reference"], "KT-DETAIL01")
        self.assertEqual(data["status"], "pending")
        self.assertEqual(data["traveller_count"], 2)
        self.assertEqual(data["price_per_person"], 150)
        self.assertEqual(data["subtotal"], 300)
        self.assertEqual(data["discount_amount"], 0)
        self.assertEqual(data["total_price"], 300)
        self.assertEqual(data["pickup_preference"], "Hotel Grand")
        self.assertEqual(data["dietary_requirements"], "Vegetarian")
        self.assertEqual(data["accessibility_needs"], "Step-free access")
        self.assertEqual(data["tour"]["id"], self.tour.id)
        self.assertEqual(data["tour"]["title"], "Taupō Lake Cruise")
        self.assertEqual(data["departure"]["id"], self.departure.id)
        self.assertTrue(data["can_cancel"])
        self.assertIsNotNone(data["cancel_deadline"])
        self.assertIsNone(data["coupon_code"])
        self.assertIsNone(data["cancelled_at"])

    def test_admin_can_view_customer_booking(self):
        response = make_client(self.admin).get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["id"], self.booking.id)

    def test_another_customer_is_forbidden(self):
        response = make_client(self.other_customer).get(self.url)

        self.assertEqual(response.status_code, 403)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], "FORBIDDEN")
        self.assertNotIn("data", payload)

    def test_anonymous_user_is_rejected(self):
        response = APIClient().get(self.url)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json()["error"]["code"],
            "UNAUTHENTICATED",
        )

    def test_missing_booking_returns_not_found(self):
        missing_id = self.booking.id + 1000
        response = self.client.get(f"/api/v1/bookings/{missing_id}")

        self.assertEqual(response.status_code, 404)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], "NOT_FOUND")

    def test_owner_can_view_every_booking_status(self):
        for booking_status in BookingStatus.values:
            with self.subTest(status=booking_status):
                Booking.objects.filter(pk=self.booking.pk).update(status=booking_status)

                response = self.client.get(self.url)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.json()["data"]["status"],
                    booking_status,
                )

    def test_detail_preserves_original_booking_price(self):
        Tour.objects.filter(pk=self.tour.pk).update(price_per_person=Decimal("200.00"))

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["price_per_person"], 150)
        self.assertEqual(data["subtotal"], 300)
        self.assertEqual(data["total_price"], 300)

    def test_viewing_details_does_not_modify_booking_or_capacity(self):
        before = Booking.objects.values().get(pk=self.booking.pk)
        count_before = Booking.objects.count()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Booking.objects.values().get(pk=self.booking.pk),
            before,
        )
        self.assertEqual(Booking.objects.count(), count_before)
        self.departure.refresh_from_db()
        self.assertEqual(self.departure.capacity, 10)
