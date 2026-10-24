"""Tests for customer booking creation.
Checks saved prices, seat reservations, permissions, and rollback.
"""

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

from apps.bookings.models import Booking, BookingStatus
from apps.bookings.services import create_booking
from apps.catalog.models import Category, Tour
from apps.core.testing import make_admin, make_client, make_customer
from apps.coupons.models import Coupon, CouponDiscountType
from apps.coupons.services import mark_coupon_used
from apps.departures.models import Departure


class BookingCreateTests(APITestCase):
    def setUp(self):
        self.customer = make_customer()
        self.client = make_client(self.customer)
        self.url = "/api/v1/bookings"

        category = Category.objects.create(name="Scenic Tours")
        self.tour = Tour.objects.create(
            title="Lake Tour",
            description="A guided lake tour.",
            location="Taupō",
            category=category,
            price_per_person=Decimal("150.00"),
            duration_days=1,
            itinerary="Meet the guide and explore the lake.",
        )
        self.departure = Departure.objects.create(
            tour=self.tour,
            start_datetime=timezone.now() + timedelta(days=30),
            booking_deadline=timezone.now() + timedelta(days=25),
            capacity=2,
        )
        self.coupon = Coupon.objects.create(
            code="SUMMER10",
            discount_type=CouponDiscountType.PERCENT,
            discount_value=Decimal("10.00"),
            expires_at=timezone.now() + timedelta(days=20),
            max_uses=1,
        )

    def book(self, **changes):
        payload = {
            "departure_id": self.departure.id,
            "traveller_count": 2,
        }
        payload.update(changes)
        return self.client.post(self.url, payload, format="json")

    def test_create_pending_booking(self):
        response = self.book()

        self.assertEqual(response.status_code, 201, response.content)
        body = response.json()
        self.assertTrue(body["success"])
        booking = Booking.objects.get(id=body["data"]["id"])
        self.assertEqual(booking.user, self.customer)
        self.assertEqual(booking.status, BookingStatus.PENDING)
        self.assertEqual(booking.traveller_count, 2)
        self.assertEqual(booking.total_price, Decimal("300.00"))
        self.assertEqual(body["data"]["total_price"], 300)
        self.assertRegex(booking.booking_reference, r"^KT-[A-Z0-9]{6}$")
        self.assertEqual(booking.pickup_preference, "")

    def test_coupon_and_preferences_are_saved(self):
        response = self.book(
            coupon_code="summer10",
            pickup_preference="Hotel Grand",
            dietary_requirements="Vegetarian",
            accessibility_needs="Step-free access",
        )

        self.assertEqual(response.status_code, 201, response.content)
        booking = Booking.objects.get()
        self.assertEqual(booking.coupon, self.coupon)
        self.assertEqual(booking.subtotal, Decimal("300.00"))
        self.assertEqual(booking.discount_amount, Decimal("30.00"))
        self.assertEqual(booking.total_price, Decimal("270.00"))
        self.assertEqual(booking.pickup_preference, "Hotel Grand")
        self.assertEqual(booking.dietary_requirements, "Vegetarian")
        self.assertEqual(booking.accessibility_needs, "Step-free access")
        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.times_used, 1)

    def test_null_preferences_become_empty_strings(self):
        response = self.book(
            pickup_preference=None,
            dietary_requirements=None,
            accessibility_needs=None,
        )

        self.assertEqual(response.status_code, 201, response.content)
        booking = Booking.objects.get()
        self.assertEqual(booking.pickup_preference, "")
        self.assertEqual(booking.dietary_requirements, "")
        self.assertEqual(booking.accessibility_needs, "")

    def test_second_booking_cannot_take_reserved_seats(self):
        first = self.book()
        second = self.book(traveller_count=1)

        self.assertEqual(first.status_code, 201, first.content)
        self.assertEqual(second.status_code, 409, second.content)
        self.assertEqual(second.json()["error"]["code"], "SEATS_UNAVAILABLE")
        self.assertEqual(Booking.objects.count(), 1)
        self.departure.refresh_from_db()
        self.assertEqual(self.departure.capacity, 2)

    def test_coupon_usage_limit_is_enforced(self):
        first = self.book(traveller_count=1, coupon_code="SUMMER10")
        second = self.book(traveller_count=1, coupon_code="SUMMER10")

        self.assertEqual(first.status_code, 201, first.content)
        self.assertEqual(second.status_code, 422, second.content)
        self.assertEqual(second.json()["error"]["code"], "COUPON_INVALID")
        self.assertEqual(Booking.objects.count(), 1)
        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.times_used, 1)

    def test_client_cannot_choose_price_status_or_owner(self):
        other_customer = make_customer(email="other@kiwitrails.test")
        response = self.book(
            total_price=1,
            price_per_person=1,
            status="approved",
            user=other_customer.id,
        )

        self.assertEqual(response.status_code, 201, response.content)
        booking = Booking.objects.get()
        self.assertEqual(booking.user, self.customer)
        self.assertEqual(booking.status, BookingStatus.PENDING)
        self.assertEqual(booking.price_per_person, Decimal("150.00"))
        self.assertEqual(booking.total_price, Decimal("300.00"))

    def test_saved_price_survives_tour_price_change(self):
        response = self.book()
        self.assertEqual(response.status_code, 201, response.content)

        self.tour.price_per_person = Decimal("200.00")
        self.tour.save()

        booking = Booking.objects.get()
        self.assertEqual(booking.price_per_person, Decimal("150.00"))
        self.assertEqual(booking.total_price, Decimal("300.00"))

    def test_invalid_input_creates_no_booking(self):
        for changes in [
            {"traveller_count": 0},
            {"traveller_count": -1},
            {"traveller_count": 1.5},
            {"pickup_preference": "x" * 256},
        ]:
            with self.subTest(changes=changes):
                response = self.book(**changes)
                self.assertEqual(response.status_code, 422, response.content)

        self.assertEqual(Booking.objects.count(), 0)

    def test_closed_departure_creates_no_booking(self):
        self.departure.booking_deadline = timezone.now() - timedelta(seconds=1)
        self.departure.save()

        response = self.book(coupon_code="SUMMER10")

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(response.json()["error"]["code"], "BOOKING_CLOSED")
        self.assertEqual(Booking.objects.count(), 0)
        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.times_used, 0)

    def test_failure_rolls_back_booking_and_coupon_usage(self):
        def fail_after_coupon_update(coupon):
            mark_coupon_used(coupon)
            raise RuntimeError("Simulated failure")

        with patch(
            "apps.bookings.services.mark_coupon_used",
            side_effect=fail_after_coupon_update,
        ):
            with self.assertRaisesRegex(RuntimeError, "Simulated failure"):
                create_booking(
                    user=self.customer,
                    departure_id=self.departure.id,
                    traveller_count=2,
                    coupon_code="SUMMER10",
                )

        self.assertEqual(Booking.objects.count(), 0)
        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.times_used, 0)

    def test_login_required(self):
        self.client = APIClient()
        response = self.book()

        self.assertEqual(response.status_code, 401, response.content)
        self.assertEqual(Booking.objects.count(), 0)

    def test_admin_cannot_create_customer_booking(self):
        self.client = make_client(make_admin())
        response = self.book()

        self.assertEqual(response.status_code, 403, response.content)
        self.assertEqual(Booking.objects.count(), 0)
