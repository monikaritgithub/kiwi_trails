"""Tests for the administrator departure attendance roster.
Checks access, booking selection, response fields, and unpaginated results.
"""

from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.bookings.models import Attendance, Booking
from apps.catalog.models import Category, Tour
from apps.core.testing import make_admin, make_client, make_customer
from apps.departures.models import Departure


class AttendanceListTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = make_admin()
        cls.customer = make_customer(
            email="aroha@example.test",
            full_name="Aroha Smith",
        )
        cls.other_customer = make_customer(
            email="tane@example.test",
            full_name="Tane Ngata",
        )

        category = Category.objects.create(name="Attendance tours")
        tour = Tour.objects.create(
            title="Lake Cruise",
            description="A scenic cruise.",
            location="Taupo",
            category=category,
            price_per_person=Decimal("100.00"),
            duration_days=1,
            itinerary="Meet at the lake.",
        )

        now = timezone.now()
        cls.departure = Departure.objects.create(
            tour=tour,
            start_datetime=now + timedelta(days=30),
            booking_deadline=now + timedelta(days=29),
            capacity=100,
        )
        cls.other_departure = Departure.objects.create(
            tour=tour,
            start_datetime=now + timedelta(days=40),
            booking_deadline=now + timedelta(days=39),
            capacity=100,
        )
        cls.empty_departure = Departure.objects.create(
            tour=tour,
            start_datetime=now + timedelta(days=50),
            booking_deadline=now + timedelta(days=49),
            capacity=100,
        )

        cls.approved = cls.make_booking("KT-ATT01", cls.customer, cls.departure, "approved")
        cls.completed = cls.make_booking("KT-ATT02", cls.other_customer, cls.departure, "completed")
        cls.absent = cls.make_booking("KT-ATT03", cls.customer, cls.departure, "approved")

        for index, status in enumerate(["pending", "rejected", "cancelled"]):
            cls.make_booking(
                f"KT-EXCLUDE{index}",
                cls.customer,
                cls.departure,
                status,
            )

        cls.other_booking = cls.make_booking(
            "KT-OTHER",
            cls.customer,
            cls.other_departure,
            "approved",
        )

        Attendance.objects.create(
            booking=cls.completed,
            status="present",
            marked_by=cls.admin,
        )
        Attendance.objects.create(
            booking=cls.absent,
            status="absent",
            marked_by=cls.admin,
        )

    @classmethod
    def make_booking(cls, reference, user, departure, status):
        return Booking.objects.create(
            booking_reference=reference,
            user=user,
            departure=departure,
            traveller_count=2,
            price_per_person=Decimal("100.00"),
            subtotal=Decimal("200.00"),
            discount_amount=Decimal("0.00"),
            total_price=Decimal("200.00"),
            status=status,
        )

    def setUp(self):
        self.client = make_client(self.admin)
        self.url = self.roster_url(self.departure.id)

    def roster_url(self, departure_id):
        return reverse(
            "admin-attendance-list",
            kwargs={"departure_id": departure_id},
        )

    def get_items(self, url=None, params=None):
        response = self.client.get(url or self.url, params or {})
        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertEqual(set(payload["data"]), {"items"})
        return payload["data"]["items"]

    def assert_error(self, response, status_code, code):
        self.assertEqual(response.status_code, status_code, response.content)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], code)

    def test_admin_gets_only_approved_and_completed_bookings(self):
        items = self.get_items()

        self.assertEqual(
            {item["booking_id"] for item in items},
            {self.approved.id, self.completed.id, self.absent.id},
        )

    def test_other_departure_bookings_are_excluded(self):
        items = self.get_items()

        self.assertNotIn(
            self.other_booking.id,
            [item["booking_id"] for item in items],
        )

    def test_response_has_exact_documented_fields(self):
        items = self.get_items()
        item = next(item for item in items if item["booking_id"] == self.approved.id)

        self.assertEqual(
            item,
            {
                "booking_id": self.approved.id,
                "booking_reference": "KT-ATT01",
                "customer_name": "Aroha Smith",
                "traveller_count": 2,
                "attendance": None,
            },
        )

    def test_present_absent_and_unmarked_attendance(self):
        items = {item["booking_id"]: item["attendance"] for item in self.get_items()}

        self.assertIsNone(items[self.approved.id])
        self.assertEqual(items[self.completed.id], "present")
        self.assertEqual(items[self.absent.id], "absent")

    def test_customer_is_forbidden_even_for_own_booking(self):
        self.client = make_client(self.customer)

        response = self.client.get(self.url)

        self.assert_error(response, 403, "FORBIDDEN")

    def test_anonymous_user_is_unauthenticated(self):
        self.client = APIClient()

        response = self.client.get(self.url)

        self.assert_error(response, 401, "UNAUTHENTICATED")

    def test_missing_departure_returns_not_found(self):
        response = self.client.get(self.roster_url(self.empty_departure.id + 10000))

        self.assert_error(response, 404, "NOT_FOUND")

    def test_departure_without_bookings_returns_empty_items(self):
        items = self.get_items(self.roster_url(self.empty_departure.id))

        self.assertEqual(items, [])

    def test_departure_without_eligible_bookings_returns_empty_items(self):
        Booking.objects.filter(departure=self.departure).update(status="pending")

        self.assertEqual(self.get_items(), [])

    def test_results_are_ordered_by_customer_name_then_booking_id(self):
        items = self.get_items()

        self.assertEqual(
            [item["booking_id"] for item in items],
            [self.approved.id, self.absent.id, self.completed.id],
        )

    def test_roster_is_not_paginated(self):
        for index in range(12):
            self.make_booking(
                f"KT-EXTRA{index}",
                self.customer,
                self.departure,
                "approved",
            )

        items = self.get_items(params={"page": 2, "page_size": 1})

        self.assertEqual(len(items), 15)
        self.assertEqual(len({item["booking_id"] for item in items}), 15)

    def test_completed_departure_roster_remains_available(self):
        Departure.objects.filter(pk=self.departure.pk).update(status="completed")

        self.assertEqual(len(self.get_items()), 3)

    def test_customer_name_supports_macrons(self):
        self.customer.full_name = "Māia Rōpata"
        self.customer.save(update_fields=["full_name"])

        items = self.get_items()
        item = next(item for item in items if item["booking_id"] == self.approved.id)

        self.assertEqual(item["customer_name"], "Māia Rōpata")

    def test_get_does_not_modify_bookings_or_attendance(self):
        bookings_before = list(Booking.objects.order_by("id").values())
        attendance_before = list(Attendance.objects.order_by("id").values())

        self.get_items()

        self.assertEqual(
            list(Booking.objects.order_by("id").values()),
            bookings_before,
        )
        self.assertEqual(
            list(Attendance.objects.order_by("id").values()),
            attendance_before,
        )
