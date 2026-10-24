"""Tests for customer calendar downloads.
Checks access, booking eligibility, UTC dates, and ICS text formatting.
"""

from datetime import datetime, timedelta
from datetime import timezone as datetime_timezone
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.bookings.documents import build_booking_calendar
from apps.bookings.models import Booking, BookingStatus
from apps.catalog.models import Category, Tour
from apps.core.testing import make_admin, make_client, make_customer
from apps.departures.models import Departure, DepartureStatus


class BookingCalendarTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = make_customer(email="calendar@kiwitrails.test")
        cls.other_customer = make_customer(email="other-calendar@kiwitrails.test")
        cls.admin = make_admin(email="calendar-admin@kiwitrails.test")

        category = Category.objects.create(name="Calendar Tours")
        cls.tour = Tour.objects.create(
            title="Taupō Lake Cruise",
            description="A guided lake cruise.",
            location="Taupō",
            category=category,
            price_per_person=Decimal("150.00"),
            duration_days=1,
            itinerary="Meet at the wharf.",
            meeting_point_name="Taupō Wharf",
        )

        now = timezone.now()
        cls.departure = Departure.objects.create(
            tour=cls.tour,
            start_datetime=now + timedelta(days=30),
            booking_deadline=now + timedelta(days=25),
            capacity=10,
            status=DepartureStatus.SCHEDULED,
        )

        cls.booking = Booking.objects.create(
            booking_reference="KT-CAL001",
            user=cls.customer,
            departure=cls.departure,
            traveller_count=2,
            price_per_person=Decimal("150.00"),
            subtotal=Decimal("300.00"),
            discount_amount=Decimal("0.00"),
            total_price=Decimal("300.00"),
            status=BookingStatus.APPROVED,
        )

    def setUp(self):
        self.client = make_client(self.customer)
        self.url = f"/api/v1/bookings/{self.booking.id}/calendar"

    def calendar_lines(self, response):
        text = response.content.decode("utf-8")
        return text.replace("\r\n ", "").split("\r\n")

    def assert_error(self, response, status_code, code):
        self.assertEqual(response.status_code, status_code)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], code)

    def test_owner_can_download_approved_booking_calendar(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        lines = self.calendar_lines(response)
        self.assertEqual(lines[0], "BEGIN:VCALENDAR")
        self.assertIn("VERSION:2.0", lines)
        self.assertIn("PRODID:-//Kiwi Trails//Tour Bookings//EN", lines)
        self.assertEqual(lines.count("BEGIN:VEVENT"), 1)
        self.assertEqual(lines.count("END:VEVENT"), 1)
        self.assertEqual(lines[-2], "END:VCALENDAR")
        self.assertEqual(lines[-1], "")

    def test_owner_can_download_pending_booking_calendar(self):
        Booking.objects.filter(pk=self.booking.pk).update(status=BookingStatus.PENDING)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_another_customer_cannot_download_calendar(self):
        with patch("apps.bookings.views.build_booking_calendar") as generator:
            response = make_client(self.other_customer).get(self.url)

        self.assert_error(response, 403, "FORBIDDEN")
        generator.assert_not_called()

    def test_admin_cannot_use_customer_calendar_endpoint(self):
        response = make_client(self.admin).get(self.url)

        self.assert_error(response, 403, "FORBIDDEN")

    def test_anonymous_request_is_rejected(self):
        response = APIClient().get(self.url)

        self.assert_error(response, 401, "UNAUTHENTICATED")

    def test_missing_booking_returns_not_found(self):
        response = self.client.get(f"/api/v1/bookings/{self.booking.id + 1000}/calendar")

        self.assert_error(response, 404, "NOT_FOUND")

    def test_terminal_booking_statuses_are_rejected(self):
        for booking_status in [
            BookingStatus.REJECTED,
            BookingStatus.CANCELLED,
            BookingStatus.COMPLETED,
        ]:
            with self.subTest(status=booking_status):
                Booking.objects.filter(pk=self.booking.pk).update(status=booking_status)

                with patch("apps.bookings.views.build_booking_calendar") as generator:
                    response = self.client.get(self.url)

                self.assert_error(response, 403, "FORBIDDEN")
                generator.assert_not_called()

    def test_unscheduled_departures_are_rejected(self):
        for departure_status in [
            DepartureStatus.CANCELLED,
            DepartureStatus.COMPLETED,
        ]:
            with self.subTest(status=departure_status):
                Departure.objects.filter(pk=self.departure.pk).update(status=departure_status)

                with patch("apps.bookings.views.build_booking_calendar") as generator:
                    response = self.client.get(self.url)

                self.assert_error(response, 403, "FORBIDDEN")
                generator.assert_not_called()

    def test_download_headers(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "text/calendar; charset=utf-8",
        )
        self.assertEqual(
            response["Content-Disposition"],
            'attachment; filename="KT-CAL001.ics"',
        )
        self.assertEqual(response["Cache-Control"], "private, no-store")

    def test_maori_title_and_meeting_point_are_preserved(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        lines = self.calendar_lines(response)
        self.assertIn("SUMMARY:Taupō Lake Cruise", lines)
        self.assertIn("LOCATION:Taupō Wharf", lines)

    def test_departure_time_is_converted_to_utc(self):
        self.departure.start_datetime = datetime(
            2030,
            12,
            1,
            9,
            30,
            tzinfo=datetime_timezone(timedelta(hours=13)),
        )
        self.booking.departure = self.departure

        content = build_booking_calendar(self.booking).decode("utf-8")

        self.assertIn("DTSTART:20301130T203000Z\r\n", content)

    def test_timestamp_is_written_in_utc(self):
        timestamp = datetime(2030, 1, 2, 3, 4, 5, tzinfo=datetime_timezone.utc)

        with patch("apps.bookings.documents.timezone") as mock_timezone:
            mock_timezone.now.return_value = timestamp
            content = build_booking_calendar(self.booking).decode("utf-8")

        self.assertIn("DTSTAMP:20300102T030405Z\r\n", content)

    def test_uid_is_stable_across_downloads(self):
        first = self.client.get(self.url)
        second = self.client.get(self.url)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        first_uid = [line for line in self.calendar_lines(first) if line.startswith("UID:")]
        second_uid = [line for line in self.calendar_lines(second) if line.startswith("UID:")]
        self.assertEqual(first_uid, ["UID:KT-CAL001@kiwi-trails"])
        self.assertEqual(first_uid, second_uid)

    def test_special_characters_cannot_inject_calendar_properties(self):
        Tour.objects.filter(pk=self.tour.pk).update(
            title="Taupō, Lake; Cruise\\Boat\nBEGIN:VEVENT",
            meeting_point_name="Wharf\r\nLOCATION:Injected",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        lines = self.calendar_lines(response)
        self.assertIn(
            "SUMMARY:Taupō\\, Lake\\; Cruise\\\\Boat\\nBEGIN:VEVENT",
            lines,
        )
        self.assertIn("LOCATION:Wharf\\nLOCATION:Injected", lines)
        self.assertEqual(lines.count("BEGIN:VEVENT"), 1)
        self.assertEqual(
            len([line for line in lines if line.startswith("LOCATION:")]),
            1,
        )

    def test_long_unicode_lines_are_folded_without_losing_characters(self):
        title = "Ō" * 140
        Tour.objects.filter(pk=self.tour.pk).update(title=title)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        physical_lines = response.content.split(b"\r\n")
        for line in physical_lines:
            self.assertLessEqual(len(line), 75)
            line.decode("utf-8")

        self.assertTrue(any(line.startswith(b" ") for line in physical_lines))
        self.assertIn(f"SUMMARY:{title}", self.calendar_lines(response))

    def test_line_endings_are_crlf(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        content = response.content
        self.assertTrue(content.endswith(b"\r\n"))
        remaining = content.replace(b"\r\n", b"")
        self.assertNotIn(b"\r", remaining)
        self.assertNotIn(b"\n", remaining)

    def test_empty_meeting_point_is_supported(self):
        Tour.objects.filter(pk=self.tour.pk).update(meeting_point_name="")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("LOCATION:", self.calendar_lines(response))

    def test_download_does_not_modify_booking_or_capacity(self):
        before = Booking.objects.values().get(pk=self.booking.pk)
        booking_count = Booking.objects.count()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Booking.objects.values().get(pk=self.booking.pk),
            before,
        )
        self.assertEqual(Booking.objects.count(), booking_count)
        self.departure.refresh_from_db()
        self.assertEqual(self.departure.capacity, 10)
