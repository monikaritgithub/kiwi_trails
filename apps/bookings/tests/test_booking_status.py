"""Tests for administrator booking status updates.
Checks transitions, permissions, seat release, and saved booking data.
"""

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.bookings.models import Booking, BookingStatus
from apps.bookings.services import update_booking_status
from apps.catalog.models import Category, Tour
from apps.core.exceptions import Forbidden
from apps.core.testing import make_admin, make_client, make_customer
from apps.coupons.models import Coupon
from apps.departures.models import Departure
from apps.departures.services import get_seats_taken


class BookingStatusTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = make_admin()
        cls.customer = make_customer()

        category = Category.objects.create(name="Status test tours")
        cls.tour = Tour.objects.create(
            title="Lake Cruise",
            description="A scenic cruise.",
            location="Taupo",
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
            booking_deadline=now + timedelta(days=29),
            capacity=2,
        )
        cls.coupon = Coupon.objects.create(
            code="STATUS10",
            discount_type="percent",
            discount_value=Decimal("10.00"),
            expires_at=now + timedelta(days=60),
            max_uses=100,
            times_used=1,
        )
        cls.booking = Booking.objects.create(
            booking_reference="KT-STATUS1",
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
        self.client = make_client(self.admin)
        self.url = reverse(
            "admin-booking-status",
            kwargs={"booking_id": self.booking.id},
        )

    def update_status(self, status, **extra):
        return self.client.patch(
            self.url,
            {"status": status, **extra},
            format="json",
        )

    def set_status(self, status):
        Booking.objects.filter(pk=self.booking.pk).update(
            status=status,
            status_reason="",
            cancelled_at=None,
        )

    def assert_error(self, response, status_code, code):
        self.assertEqual(response.status_code, status_code, response.content)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], code)

    def test_all_allowed_transitions_succeed(self):
        transitions = [
            ("pending", "approved"),
            ("pending", "rejected"),
            ("pending", "cancelled"),
            ("approved", "cancelled"),
            ("approved", "completed"),
        ]

        for source, target in transitions:
            with self.subTest(source=source, target=target):
                self.set_status(source)

                response = self.update_status(target)

                self.assertEqual(response.status_code, 200, response.content)
                self.assertTrue(response.json()["success"])
                self.assertEqual(response.json()["data"]["status"], target)

                self.booking.refresh_from_db()
                self.assertEqual(self.booking.status, target)

    def test_all_disallowed_transitions_are_rejected(self):
        allowed = {
            ("pending", "approved"),
            ("pending", "rejected"),
            ("pending", "cancelled"),
            ("approved", "cancelled"),
            ("approved", "completed"),
        }
        targets = ["approved", "rejected", "cancelled", "completed"]

        for source in BookingStatus.values:
            for target in targets:
                if (source, target) in allowed:
                    continue

                with self.subTest(source=source, target=target):
                    self.set_status(source)

                    response = self.update_status(target)

                    self.assert_error(response, 409, "INVALID_STATUS_CHANGE")
                    self.booking.refresh_from_db()
                    self.assertEqual(self.booking.status, source)

    def test_response_contains_full_admin_booking_details(self):
        response = self.update_status("approved")
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]

        self.assertEqual(data["id"], self.booking.id)
        self.assertEqual(data["booking_reference"], "KT-STATUS1")
        self.assertEqual(data["customer"]["id"], self.customer.id)
        self.assertEqual(data["customer"]["email"], self.customer.email)
        self.assertEqual(data["tour"]["id"], self.tour.id)
        self.assertEqual(data["departure"]["id"], self.departure.id)
        self.assertIsNone(data["attendance"])
        self.assertEqual(Decimal(str(data["total_price"])), Decimal("270.00"))

    def test_customer_cannot_change_status(self):
        self.client = make_client(self.customer)

        response = self.update_status("approved")

        self.assert_error(response, 403, "FORBIDDEN")
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, BookingStatus.PENDING)

    def test_anonymous_user_cannot_change_status(self):
        self.client = APIClient()

        response = self.update_status("approved")

        self.assert_error(response, 401, "UNAUTHENTICATED")

    def test_missing_booking_returns_not_found(self):
        self.url = reverse(
            "admin-booking-status",
            kwargs={"booking_id": self.booking.id + 10000},
        )

        response = self.update_status("approved")

        self.assert_error(response, 404, "NOT_FOUND")

    def test_status_is_required(self):
        response = self.client.patch(self.url, {}, format="json")

        self.assert_error(response, 422, "VALIDATION_ERROR")

    def test_invalid_status_values_are_rejected(self):
        for value in ["pending", "unknown", "APPROVED", "", None, 123]:
            with self.subTest(value=value):
                response = self.update_status(value)
                self.assert_error(response, 422, "VALIDATION_ERROR")

        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, BookingStatus.PENDING)

    def test_reason_is_trimmed_and_saved(self):
        response = self.update_status(
            "rejected",
            reason="  Unable to accommodate this booking.  ",
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.booking.refresh_from_db()
        self.assertEqual(
            self.booking.status_reason,
            "Unable to accommodate this booking.",
        )
        self.assertEqual(
            response.json()["data"]["status_reason"],
            self.booking.status_reason,
        )

    def test_optional_blank_and_null_reasons_are_accepted(self):
        for extra in [{}, {"reason": ""}, {"reason": None}, {"reason": "   "}]:
            with self.subTest(extra=extra):
                self.set_status("pending")

                response = self.update_status("rejected", **extra)

                self.assertEqual(response.status_code, 200, response.content)
                self.booking.refresh_from_db()
                self.assertEqual(self.booking.status_reason, "")
                self.assertIsNone(response.json()["data"]["status_reason"])

    def test_reason_length_limit(self):
        response = self.update_status("rejected", reason="x" * 256)

        self.assert_error(response, 422, "VALIDATION_ERROR")
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, BookingStatus.PENDING)

        response = self.update_status("rejected", reason="x" * 255)

        self.assertEqual(response.status_code, 200, response.content)
        self.booking.refresh_from_db()
        self.assertEqual(len(self.booking.status_reason), 255)

    def test_admin_can_cancel_after_customer_deadline(self):
        Departure.objects.filter(pk=self.departure.pk).update(
            start_datetime=timezone.now() + timedelta(days=1)
        )
        self.set_status("approved")

        response = self.update_status("cancelled", reason="Operator cancellation")

        self.assertEqual(response.status_code, 200, response.content)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, BookingStatus.CANCELLED)
        self.assertIsNotNone(self.booking.cancelled_at)
        self.assertFalse(response.json()["data"]["can_cancel"])

    def test_cancellation_sets_timestamp(self):
        before = timezone.now()

        response = self.update_status("cancelled")

        after = timezone.now()
        self.assertEqual(response.status_code, 200, response.content)
        self.booking.refresh_from_db()
        self.assertGreaterEqual(self.booking.cancelled_at, before)
        self.assertLessEqual(self.booking.cancelled_at, after)

    def test_non_cancellation_changes_leave_cancelled_at_null(self):
        for source, target in [
            ("pending", "approved"),
            ("pending", "rejected"),
            ("approved", "completed"),
        ]:
            with self.subTest(source=source, target=target):
                self.set_status(source)

                response = self.update_status(target)

                self.assertEqual(response.status_code, 200, response.content)
                self.booking.refresh_from_db()
                self.assertIsNone(self.booking.cancelled_at)

    def test_rejection_and_cancellation_release_seats_without_changing_capacity(self):
        for source, target in [
            ("pending", "rejected"),
            ("pending", "cancelled"),
            ("approved", "cancelled"),
        ]:
            with self.subTest(source=source, target=target):
                self.set_status(source)
                self.assertEqual(get_seats_taken(self.departure), 2)

                response = self.update_status(target)

                self.assertEqual(response.status_code, 200, response.content)
                self.assertEqual(get_seats_taken(self.departure), 0)
                self.departure.refresh_from_db()
                self.assertEqual(self.departure.capacity, 2)

    def test_approval_and_completion_keep_seats_reserved(self):
        for source, target in [
            ("pending", "approved"),
            ("approved", "completed"),
        ]:
            with self.subTest(source=source, target=target):
                self.set_status(source)

                response = self.update_status(target)

                self.assertEqual(response.status_code, 200, response.content)
                self.assertEqual(get_seats_taken(self.departure), 2)

    def test_prices_and_coupon_usage_are_preserved(self):
        for target in ["approved", "rejected", "cancelled"]:
            with self.subTest(target=target):
                self.set_status("pending")

                response = self.update_status(target)

                self.assertEqual(response.status_code, 200, response.content)
                self.booking.refresh_from_db()
                self.coupon.refresh_from_db()
                self.assertEqual(self.booking.price_per_person, Decimal("150.00"))
                self.assertEqual(self.booking.subtotal, Decimal("300.00"))
                self.assertEqual(self.booking.discount_amount, Decimal("30.00"))
                self.assertEqual(self.booking.total_price, Decimal("270.00"))
                self.assertEqual(self.booking.coupon_id, self.coupon.id)
                self.assertEqual(self.coupon.times_used, 1)

    def test_repeated_cancellation_preserves_original_reason_and_timestamp(self):
        response = self.update_status("cancelled", reason="Original reason")
        self.assertEqual(response.status_code, 200, response.content)

        self.booking.refresh_from_db()
        cancelled_at = self.booking.cancelled_at

        response = self.update_status("cancelled", reason="Replacement reason")

        self.assert_error(response, 409, "INVALID_STATUS_CHANGE")
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status_reason, "Original reason")
        self.assertEqual(self.booking.cancelled_at, cancelled_at)

    def test_service_rejects_customer_directly(self):
        with self.assertRaises(Forbidden):
            update_booking_status(
                user=self.customer,
                booking_id=self.booking.id,
                status="approved",
            )

        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, BookingStatus.PENDING)

    def test_failure_rolls_back_status_change(self):
        original_save = Booking.save

        def save_then_fail(instance, *args, **kwargs):
            original_save(instance, *args, **kwargs)
            raise RuntimeError("Simulated failure after save")

        with patch("apps.bookings.models.Booking.save", new=save_then_fail):
            with self.assertRaisesRegex(RuntimeError, "Simulated failure"):
                update_booking_status(
                    user=self.admin,
                    booking_id=self.booking.id,
                    status="cancelled",
                    reason="Should be rolled back",
                )

        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, BookingStatus.PENDING)
        self.assertEqual(self.booking.status_reason, "")
        self.assertIsNone(self.booking.cancelled_at)
        self.assertEqual(get_seats_taken(self.departure), 2)
