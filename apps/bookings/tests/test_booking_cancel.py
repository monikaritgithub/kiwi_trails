"""Tests for customer booking cancellation.
Checks permissions, deadlines, seat release, and preserved booking data.
"""

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.bookings.models import Booking, BookingStatus
from apps.catalog.models import Category, Tour
from apps.core.testing import make_admin, make_client, make_customer
from apps.coupons.models import Coupon
from apps.departures.models import Departure
from apps.departures.services import get_seats_taken


class BookingCancelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = make_customer(email="cancel@kiwitrails.test")
        cls.other_customer = make_customer(email="other-cancel@kiwitrails.test")
        cls.admin = make_admin(email="cancel-admin@kiwitrails.test")

        category = Category.objects.create(name="Cancellation Tours")
        cls.tour = Tour.objects.create(
            title="Taupō Lake Cruise",
            description="A guided lake cruise.",
            location="Taupō",
            category=category,
            price_per_person=Decimal("150.00"),
            duration_days=1,
            itinerary="Meet at the lake.",
            cancellation_days=7,
        )

        now = timezone.now()
        cls.departure = Departure.objects.create(
            tour=cls.tour,
            start_datetime=now + timedelta(days=30),
            booking_deadline=now + timedelta(days=25),
            capacity=2,
        )

        cls.coupon = Coupon.objects.create(
            code="CANCEL10",
            discount_type="percent",
            discount_value=Decimal("10.00"),
            expires_at=now + timedelta(days=20),
            max_uses=10,
            times_used=1,
            is_active=True,
        )

        cls.booking = Booking.objects.create(
            booking_reference="KT-CANCEL01",
            user=cls.customer,
            departure=cls.departure,
            traveller_count=2,
            price_per_person=Decimal("150.00"),
            subtotal=Decimal("300.00"),
            discount_amount=Decimal("30.00"),
            total_price=Decimal("270.00"),
            coupon=cls.coupon,
            status=BookingStatus.PENDING,
        )

    def setUp(self):
        self.client = make_client(self.customer)
        self.url = f"/api/v1/bookings/{self.booking.id}/cancel"

    def cancel(self, payload=None):
        return self.client.post(
            self.url,
            payload if payload is not None else {},
            format="json",
        )

    def assert_error(self, response, status_code, code):
        self.assertEqual(response.status_code, status_code)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], code)

    def test_owner_can_cancel_pending_booking_with_reason(self):
        response = self.cancel({"reason": "Change of plans"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        data = payload["data"]
        self.assertEqual(data["id"], self.booking.id)
        self.assertEqual(data["status"], "cancelled")
        self.assertEqual(data["status_reason"], "Change of plans")
        self.assertIsNotNone(data["cancelled_at"])
        self.assertFalse(data["can_cancel"])

        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, BookingStatus.CANCELLED)
        self.assertEqual(self.booking.status_reason, "Change of plans")
        self.assertIsNotNone(self.booking.cancelled_at)

    def test_owner_can_cancel_approved_booking(self):
        Booking.objects.filter(pk=self.booking.pk).update(status=BookingStatus.APPROVED)

        response = self.cancel()

        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, BookingStatus.CANCELLED)

    def test_reason_is_optional(self):
        response = self.cancel()

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["data"]["status_reason"])

    def test_null_reason_is_accepted(self):
        response = self.cancel({"reason": None})

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["data"]["status_reason"])

    def test_reason_is_trimmed(self):
        response = self.cancel({"reason": "  Change of plans  "})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["data"]["status_reason"],
            "Change of plans",
        )

    def test_reason_over_255_characters_is_rejected(self):
        response = self.cancel({"reason": "x" * 256})

        self.assert_error(response, 422, "VALIDATION_ERROR")
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, BookingStatus.PENDING)
        self.assertIsNone(self.booking.cancelled_at)

    def test_another_customer_cannot_cancel_booking(self):
        self.client = make_client(self.other_customer)
        response = self.cancel()

        self.assert_error(response, 403, "FORBIDDEN")
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, BookingStatus.PENDING)

    def test_admin_cannot_use_customer_cancellation_endpoint(self):
        self.client = make_client(self.admin)
        response = self.cancel()

        self.assert_error(response, 403, "FORBIDDEN")
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, BookingStatus.PENDING)

    def test_anonymous_request_is_rejected(self):
        self.client = APIClient()
        response = self.cancel()

        self.assert_error(response, 401, "UNAUTHENTICATED")

    def test_missing_booking_returns_not_found(self):
        self.url = f"/api/v1/bookings/{self.booking.id + 1000}/cancel"
        response = self.cancel()

        self.assert_error(response, 404, "NOT_FOUND")

    def test_terminal_statuses_cannot_be_cancelled(self):
        for booking_status in [
            BookingStatus.REJECTED,
            BookingStatus.CANCELLED,
            BookingStatus.COMPLETED,
        ]:
            with self.subTest(status=booking_status):
                Booking.objects.filter(pk=self.booking.pk).update(status=booking_status)

                response = self.cancel()

                self.assert_error(response, 409, "INVALID_STATUS_CHANGE")
                self.booking.refresh_from_db()
                self.assertEqual(self.booking.status, booking_status)

    def test_cancellation_before_deadline_is_allowed(self):
        deadline = self.departure.start_datetime - timedelta(days=7)
        cancellation_time = deadline - timedelta(seconds=1)

        with patch("apps.bookings.services.timezone") as mock_timezone:
            mock_timezone.now.return_value = cancellation_time
            response = self.cancel()

        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, BookingStatus.CANCELLED)
        self.assertEqual(self.booking.cancelled_at, cancellation_time)

    def test_cancellation_at_deadline_is_rejected(self):
        deadline = self.departure.start_datetime - timedelta(days=7)

        with patch("apps.bookings.services.timezone") as mock_timezone:
            mock_timezone.now.return_value = deadline
            response = self.cancel()

        self.assert_error(response, 409, "CANCELLATION_NOT_ALLOWED")
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, BookingStatus.PENDING)
        self.assertIsNone(self.booking.cancelled_at)

    def test_cancellation_after_deadline_is_rejected(self):
        deadline = self.departure.start_datetime - timedelta(days=7)

        with patch("apps.bookings.services.timezone") as mock_timezone:
            mock_timezone.now.return_value = deadline + timedelta(seconds=1)
            response = self.cancel()

        self.assert_error(response, 409, "CANCELLATION_NOT_ALLOWED")
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, BookingStatus.PENDING)
        self.assertIsNone(self.booking.cancelled_at)

    def test_cancellation_releases_seats_without_increasing_capacity(self):
        self.assertEqual(get_seats_taken(self.departure), 2)

        response = self.cancel()

        self.assertEqual(response.status_code, 200)
        self.departure.refresh_from_db()
        self.assertEqual(self.departure.capacity, 2)
        self.assertEqual(get_seats_taken(self.departure), 0)

    def test_cancellation_preserves_prices_and_coupon_usage(self):
        response = self.cancel()

        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.coupon.refresh_from_db()

        self.assertEqual(self.booking.price_per_person, Decimal("150.00"))
        self.assertEqual(self.booking.subtotal, Decimal("300.00"))
        self.assertEqual(self.booking.discount_amount, Decimal("30.00"))
        self.assertEqual(self.booking.total_price, Decimal("270.00"))
        self.assertEqual(self.booking.coupon_id, self.coupon.id)
        self.assertEqual(self.coupon.times_used, 1)

    def test_repeated_cancellation_preserves_first_cancellation(self):
        first_response = self.cancel({"reason": "Original reason"})
        self.assertEqual(first_response.status_code, 200)
        self.booking.refresh_from_db()
        first_cancelled_at = self.booking.cancelled_at

        second_response = self.cancel({"reason": "Replacement reason"})

        self.assert_error(second_response, 409, "INVALID_STATUS_CHANGE")
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status_reason, "Original reason")
        self.assertEqual(self.booking.cancelled_at, first_cancelled_at)
        self.assertEqual(get_seats_taken(self.departure), 0)
