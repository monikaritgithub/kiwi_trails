"""Tests for booking price previews.
Checks prices, permissions, availability, and unchanged booking data.
"""

from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

from apps.bookings.models import Booking, BookingStatus
from apps.catalog.models import Category, Tour, TourStatus
from apps.core.testing import make_admin, make_client, make_customer
from apps.coupons.models import Coupon, CouponDiscountType
from apps.departures.models import Departure, DepartureStatus


class BookingQuoteTests(APITestCase):
    def setUp(self):
        self.customer = make_customer()
        self.client = make_client(self.customer)
        self.url = "/api/v1/bookings/quote"

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
            capacity=10,
        )

        self.coupon = Coupon.objects.create(
            code="SUMMER10",
            discount_type=CouponDiscountType.PERCENT,
            discount_value=Decimal("10.00"),
            expires_at=timezone.now() + timedelta(days=20),
            max_uses=100,
        )

    def quote(self, **changes):
        payload = {
            "departure_id": self.departure.id,
            "traveller_count": 2,
        }
        payload.update(changes)
        return self.client.post(self.url, payload, format="json")

    def assert_api_error(self, response, status_code, code):
        self.assertEqual(response.status_code, status_code, response.content)
        body = response.json()
        self.assertFalse(body["success"])
        self.assertEqual(body["error"]["code"], code)

    def test_quote_without_coupon(self):
        response = self.quote()

        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["data"]["subtotal"], 300)
        self.assertEqual(body["data"]["discount_amount"], 0)
        self.assertEqual(body["data"]["total_price"], 300)
        self.assertEqual(body["data"]["seats_left"], 10)
        self.assertIsNone(body["data"]["coupon_code"])

    def test_quote_with_coupon_does_not_change_data(self):
        booking_count = Booking.objects.count()
        original_usage = self.coupon.times_used

        response = self.quote(coupon_code=" summer10 ")

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["subtotal"], 300)
        self.assertEqual(data["discount_amount"], 30)
        self.assertEqual(data["total_price"], 270)
        self.assertEqual(data["coupon_code"], "SUMMER10")
        self.assertEqual(Booking.objects.count(), booking_count)

        self.coupon.refresh_from_db()
        self.departure.refresh_from_db()
        self.assertEqual(self.coupon.times_used, original_usage)
        self.assertEqual(self.departure.capacity, 10)
        self.assertEqual(self.quote().json()["data"]["seats_left"], 10)

    def test_fixed_discount_cannot_exceed_subtotal(self):
        self.coupon.discount_type = CouponDiscountType.FIXED
        self.coupon.discount_value = Decimal("500.00")
        self.coupon.save()

        response = self.quote(coupon_code=self.coupon.code)

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["discount_amount"], 300)
        self.assertEqual(data["total_price"], 0)

    def test_discount_rounds_half_up(self):
        self.tour.price_per_person = Decimal("10.05")
        self.tour.save()

        response = self.quote(traveller_count=1, coupon_code=self.coupon.code)

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["discount_amount"], 1.01)
        self.assertEqual(data["total_price"], 9.04)

    def test_invalid_traveller_counts(self):
        for count in [0, -1, 1.5, "invalid", None]:
            with self.subTest(count=count):
                response = self.quote(traveller_count=count)
                self.assert_api_error(response, 422, "VALIDATION_ERROR")

    def test_missing_required_fields(self):
        response = self.client.post(self.url, {}, format="json")
        self.assert_api_error(response, 422, "VALIDATION_ERROR")

    def test_missing_departure(self):
        missing_id = self.departure.id + 1000
        response = self.quote(departure_id=missing_id)
        self.assert_api_error(response, 404, "NOT_FOUND")

    def test_unknown_coupon(self):
        response = self.quote(coupon_code="UNKNOWN")
        self.assert_api_error(response, 422, "COUPON_INVALID")

    def test_expired_coupon(self):
        self.coupon.expires_at = timezone.now() - timedelta(seconds=1)
        self.coupon.save()

        response = self.quote(coupon_code=self.coupon.code)
        self.assert_api_error(response, 422, "COUPON_INVALID")

    def test_inactive_coupon(self):
        self.coupon.is_active = False
        self.coupon.save()

        response = self.quote(coupon_code=self.coupon.code)
        self.assert_api_error(response, 422, "COUPON_INVALID")

    def test_used_up_coupon(self):
        self.coupon.times_used = self.coupon.max_uses
        self.coupon.save()

        response = self.quote(coupon_code=self.coupon.code)
        self.assert_api_error(response, 422, "COUPON_INVALID")

    def test_insufficient_seats(self):
        response = self.quote(traveller_count=11)
        self.assert_api_error(response, 409, "SEATS_UNAVAILABLE")

    def test_booking_status_controls_available_seats(self):
        booking = Booking.objects.create(
            booking_reference="KT-TEST01",
            user=self.customer,
            departure=self.departure,
            traveller_count=10,
            price_per_person=Decimal("150.00"),
            subtotal=Decimal("1500.00"),
            total_price=Decimal("1500.00"),
        )

        for status in [
            BookingStatus.PENDING,
            BookingStatus.APPROVED,
            BookingStatus.COMPLETED,
        ]:
            with self.subTest(status=status):
                booking.status = status
                booking.save()
                self.assert_api_error(self.quote(), 409, "SEATS_UNAVAILABLE")

        for status in [BookingStatus.REJECTED, BookingStatus.CANCELLED]:
            with self.subTest(status=status):
                booking.status = status
                booking.save()
                response = self.quote()
                self.assertEqual(response.status_code, 200, response.content)
                self.assertEqual(response.json()["data"]["seats_left"], 10)

    def test_booking_deadline_has_passed(self):
        self.departure.booking_deadline = timezone.now() - timedelta(seconds=1)
        self.departure.save()

        self.assert_api_error(self.quote(), 409, "BOOKING_CLOSED")

    def test_archived_tour(self):
        self.tour.status = TourStatus.ARCHIVED
        self.tour.save()

        self.assert_api_error(self.quote(), 409, "BOOKING_CLOSED")

    def test_departure_not_scheduled(self):
        for status in [DepartureStatus.CANCELLED, DepartureStatus.COMPLETED]:
            with self.subTest(status=status):
                self.departure.status = status
                self.departure.save()
                self.assert_api_error(self.quote(), 409, "BOOKING_CLOSED")

    def test_login_required(self):
        self.client = APIClient()
        self.assert_api_error(self.quote(), 401, "UNAUTHENTICATED")

    def test_admin_cannot_request_customer_quote(self):
        self.client = make_client(make_admin())
        self.assert_api_error(self.quote(), 403, "FORBIDDEN")
