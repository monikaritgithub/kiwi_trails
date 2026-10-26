"""Tests for administrator booking attendance updates.
Checks permissions, validation, repeat updates, and saved audit information.
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


class AttendanceUpdateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = make_admin()
        cls.other_admin = make_admin(email="attendance-admin@example.test")
        cls.customer = make_customer(
            email="attendance-customer@example.test",
            full_name="Aroha Smith",
        )

        category = Category.objects.create(name="Attendance update tours")
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

        cls.booking = Booking.objects.create(
            booking_reference="KT-MARK01",
            user=cls.customer,
            departure=cls.departure,
            traveller_count=2,
            price_per_person=Decimal("100.00"),
            subtotal=Decimal("200.00"),
            discount_amount=Decimal("0.00"),
            total_price=Decimal("200.00"),
            status="approved",
        )

    def setUp(self):
        self.client = make_client(self.admin)
        self.url = reverse(
            "admin-attendance-update",
            kwargs={"booking_id": self.booking.pk},
        )

    def put_status(self, status):
        return self.client.put(
            self.url,
            {"status": status},
            format="json",
        )

    def assert_error(self, response, status_code, code):
        self.assertEqual(response.status_code, status_code, response.content)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], code)

    def create_attendance(self, status="present"):
        return Attendance.objects.create(
            booking=self.booking,
            status=status,
            marked_by=self.admin,
        )

    def test_admin_can_mark_approved_booking_present(self):
        response = self.put_status("present")

        self.assertEqual(response.status_code, 200, response.content)
        attendance = Attendance.objects.get(booking=self.booking)
        self.assertEqual(attendance.status, "present")
        self.assertEqual(attendance.marked_by_id, self.admin.pk)

    def test_admin_can_mark_approved_booking_absent(self):
        response = self.put_status("absent")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            Attendance.objects.get(booking=self.booking).status,
            "absent",
        )

    def test_completed_booking_can_be_marked(self):
        Booking.objects.filter(pk=self.booking.pk).update(status="completed")

        response = self.put_status("present")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            Attendance.objects.get(booking=self.booking).status,
            "present",
        )

    def test_response_matches_documented_fields(self):
        response = self.put_status("present")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            response.json(),
            {
                "success": True,
                "data": {
                    "booking_id": self.booking.pk,
                    "booking_reference": "KT-MARK01",
                    "customer_name": "Aroha Smith",
                    "traveller_count": 2,
                    "attendance": "present",
                },
            },
        )

    def test_ineligible_booking_statuses_are_rejected(self):
        for status in ["pending", "rejected", "cancelled"]:
            with self.subTest(status=status):
                Booking.objects.filter(pk=self.booking.pk).update(status=status)

                response = self.put_status("present")

                self.assert_error(response, 422, "VALIDATION_ERROR")
                self.assertFalse(Attendance.objects.filter(booking=self.booking).exists())

    def test_customer_cannot_mark_own_booking(self):
        self.client = make_client(self.customer)

        response = self.put_status("present")

        self.assert_error(response, 403, "FORBIDDEN")
        self.assertFalse(Attendance.objects.exists())

    def test_anonymous_request_is_rejected(self):
        self.client = APIClient()

        response = self.put_status("present")

        self.assert_error(response, 401, "UNAUTHENTICATED")
        self.assertFalse(Attendance.objects.exists())

    def test_missing_booking_returns_not_found(self):
        url = reverse(
            "admin-attendance-update",
            kwargs={"booking_id": self.booking.pk + 10000},
        )

        response = self.client.put(url, {"status": "present"}, format="json")

        self.assert_error(response, 404, "NOT_FOUND")
        self.assertFalse(Attendance.objects.exists())

    def test_missing_status_is_rejected(self):
        response = self.client.put(self.url, {}, format="json")

        self.assert_error(response, 422, "VALIDATION_ERROR")
        self.assertFalse(Attendance.objects.exists())

    def test_invalid_status_values_are_rejected(self):
        for value in ["late", "approved", "", None, 123, [], {}]:
            with self.subTest(value=value):
                response = self.put_status(value)

                self.assert_error(response, 422, "VALIDATION_ERROR")
                self.assertFalse(Attendance.objects.exists())

    def test_attendance_key_does_not_replace_required_status(self):
        response = self.client.put(
            self.url,
            {"attendance": "present"},
            format="json",
        )

        self.assert_error(response, 422, "VALIDATION_ERROR")
        self.assertFalse(Attendance.objects.exists())

    def test_present_can_be_changed_to_absent(self):
        attendance = self.create_attendance("present")

        response = self.put_status("absent")

        self.assertEqual(response.status_code, 200, response.content)
        attendance.refresh_from_db()
        self.assertEqual(attendance.status, "absent")
        self.assertEqual(response.json()["data"]["attendance"], "absent")
        self.assertEqual(
            Attendance.objects.get(booking=self.booking).pk,
            attendance.pk,
        )
        self.assertEqual(Attendance.objects.count(), 1)

    def test_absent_can_be_changed_to_present(self):
        attendance = self.create_attendance("absent")

        response = self.put_status("present")

        self.assertEqual(response.status_code, 200, response.content)
        attendance.refresh_from_db()
        self.assertEqual(attendance.status, "present")
        self.assertEqual(response.json()["data"]["attendance"], "present")
        self.assertEqual(Attendance.objects.count(), 1)

    def test_repeating_same_status_does_not_create_duplicate(self):
        attendance = self.create_attendance("present")

        response = self.put_status("present")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(Attendance.objects.count(), 1)
        self.assertEqual(
            Attendance.objects.get(booking=self.booking).pk,
            attendance.pk,
        )

    def test_latest_admin_is_saved_as_marked_by(self):
        attendance = self.create_attendance("present")
        self.client = make_client(self.other_admin)

        response = self.put_status("absent")

        self.assertEqual(response.status_code, 200, response.content)
        attendance.refresh_from_db()
        self.assertEqual(attendance.marked_by_id, self.other_admin.pk)

    def test_marked_at_is_set_on_creation(self):
        before = timezone.now()

        response = self.put_status("present")

        after = timezone.now()
        self.assertEqual(response.status_code, 200, response.content)
        attendance = Attendance.objects.get(booking=self.booking)
        self.assertGreaterEqual(attendance.marked_at, before)
        self.assertLessEqual(attendance.marked_at, after)

    def test_marked_at_updates_when_mark_is_saved_again(self):
        attendance = self.create_attendance("present")
        old_time = timezone.now() - timedelta(days=1)
        Attendance.objects.filter(pk=attendance.pk).update(marked_at=old_time)
        before = timezone.now()

        response = self.put_status("present")

        after = timezone.now()
        self.assertEqual(response.status_code, 200, response.content)
        attendance.refresh_from_db()
        self.assertGreater(attendance.marked_at, old_time)
        self.assertGreaterEqual(attendance.marked_at, before)
        self.assertLessEqual(attendance.marked_at, after)

    def test_client_cannot_override_audit_fields(self):
        before = timezone.now()

        response = self.client.put(
            self.url,
            {
                "status": "present",
                "marked_by": self.other_admin.pk,
                "marked_at": "2000-01-01T00:00:00Z",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200, response.content)
        attendance = Attendance.objects.get(booking=self.booking)
        self.assertEqual(attendance.marked_by_id, self.admin.pk)
        self.assertGreaterEqual(attendance.marked_at, before)

    def test_invalid_update_preserves_existing_attendance(self):
        self.create_attendance("present")
        before = Attendance.objects.get(booking=self.booking)
        original = (before.status, before.marked_by_id, before.marked_at)

        response = self.put_status("late")

        self.assert_error(response, 422, "VALIDATION_ERROR")
        before.refresh_from_db()
        self.assertEqual(
            (before.status, before.marked_by_id, before.marked_at),
            original,
        )

    def test_ineligible_booking_preserves_existing_attendance(self):
        attendance = self.create_attendance("present")
        original_time = attendance.marked_at
        Booking.objects.filter(pk=self.booking.pk).update(status="cancelled")

        response = self.put_status("absent")

        self.assert_error(response, 422, "VALIDATION_ERROR")
        attendance.refresh_from_db()
        self.assertEqual(attendance.status, "present")
        self.assertEqual(attendance.marked_at, original_time)

    def test_marking_does_not_modify_booking_or_departure(self):
        booking_before = Booking.objects.filter(pk=self.booking.pk).values().get()
        departure_before = Departure.objects.filter(pk=self.departure.pk).values().get()

        response = self.put_status("present")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            Booking.objects.filter(pk=self.booking.pk).values().get(),
            booking_before,
        )
        self.assertEqual(
            Departure.objects.filter(pk=self.departure.pk).values().get(),
            departure_before,
        )

    def test_updated_attendance_is_visible_in_roster(self):
        response = self.put_status("absent")
        self.assertEqual(response.status_code, 200, response.content)
        roster_url = reverse(
            "admin-attendance-list",
            kwargs={"departure_id": self.departure.pk},
        )

        response = self.client.get(roster_url)

        self.assertEqual(response.status_code, 200, response.content)
        item = next(
            item
            for item in response.json()["data"]["items"]
            if item["booking_id"] == self.booking.pk
        )
        self.assertEqual(item["attendance"], "absent")
