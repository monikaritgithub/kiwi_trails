"""Tests for the administrator booking list.
Checks permissions, filters, pagination, and customer attendance details.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.bookings.models import Attendance, Booking, BookingStatus
from apps.catalog.models import Category, Tour
from apps.core.testing import make_admin, make_client, make_customer
from apps.departures.models import Departure


class AdminBookingListTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = make_admin()
        cls.customer = make_customer(
            email="aroha@example.test",
            full_name="Aroha Smith",
        )
        cls.other_customer = make_customer(
            email="mia@example.test",
            full_name="Mia Brown",
        )
        cls.customer.phone = "0211234567"
        cls.customer.save(update_fields=["phone"])

        category = Category.objects.create(name="Admin booking tours")
        cls.tour = Tour.objects.create(
            title="Taupo Lake Cruise",
            description="A scenic lake cruise.",
            location="Taupo",
            category=category,
            price_per_person=Decimal("150.00"),
            duration_days=1,
            itinerary="Meet at the lake.",
        )
        cls.other_tour = Tour.objects.create(
            title="Rotorua Walk",
            description="A guided walking tour.",
            location="Rotorua",
            category=category,
            price_per_person=Decimal("100.00"),
            duration_days=1,
            itinerary="Meet at the entrance.",
        )

        cls.departure = Departure.objects.create(
            tour=cls.tour,
            start_datetime=datetime(2030, 6, 10, 10, tzinfo=timezone.utc),
            booking_deadline=datetime(2030, 6, 9, tzinfo=timezone.utc),
            capacity=100,
        )
        cls.other_departure = Departure.objects.create(
            tour=cls.other_tour,
            start_datetime=datetime(2030, 6, 20, 10, tzinfo=timezone.utc),
            booking_deadline=datetime(2030, 6, 19, tzinfo=timezone.utc),
            capacity=100,
        )

        cls.pending = cls.make_booking(
            "KT-ADMIN01",
            cls.customer,
            cls.departure,
            BookingStatus.PENDING,
        )
        cls.approved = cls.make_booking(
            "KT-ADMIN02",
            cls.other_customer,
            cls.other_departure,
            BookingStatus.APPROVED,
        )
        cls.completed = cls.make_booking(
            "KT-ADMIN03",
            cls.customer,
            cls.departure,
            BookingStatus.COMPLETED,
        )

        Attendance.objects.create(
            booking=cls.approved,
            status="present",
            marked_by=cls.admin,
        )
        Attendance.objects.create(
            booking=cls.completed,
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
            price_per_person=Decimal("150.00"),
            subtotal=Decimal("300.00"),
            discount_amount=Decimal("30.00"),
            total_price=Decimal("270.00"),
            status=status,
        )

    def setUp(self):
        self.client = make_client(self.admin)
        self.url = reverse("admin-booking-list")

    def get_data(self, params=None):
        response = self.client.get(self.url, params or {})
        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        self.assertTrue(payload["success"])
        return payload["data"]

    def get_ids(self, params=None):
        return [item["id"] for item in self.get_data(params)["items"]]

    def assert_error(self, response, status_code, code):
        self.assertEqual(response.status_code, status_code, response.content)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], code)

    def test_admin_can_list_bookings_from_multiple_customers(self):
        data = self.get_data()

        self.assertEqual(data["total"], 3)
        self.assertEqual(
            {item["customer"]["id"] for item in data["items"]},
            {self.customer.id, self.other_customer.id},
        )

    def test_customer_cannot_access_admin_list(self):
        self.client = make_client(self.customer)

        response = self.client.get(self.url)

        self.assert_error(response, 403, "FORBIDDEN")

    def test_anonymous_user_cannot_access_admin_list(self):
        self.client = APIClient()

        response = self.client.get(self.url)

        self.assert_error(response, 401, "UNAUTHENTICATED")

    def test_response_contains_customer_details_and_saved_prices(self):
        data = self.get_data({"search": self.pending.booking_reference})
        item = data["items"][0]

        self.assertEqual(
            item["customer"],
            {
                "id": self.customer.id,
                "full_name": "Aroha Smith",
                "email": "aroha@example.test",
                "phone": "0211234567",
            },
        )
        self.assertEqual(item["booking_reference"], "KT-ADMIN01")
        self.assertEqual(item["tour"]["id"], self.tour.id)
        self.assertEqual(item["departure"]["id"], self.departure.id)
        self.assertEqual(Decimal(str(item["total_price"])), Decimal("270.00"))
        self.assertNotIn("password", item["customer"])

    def test_attendance_is_present_absent_or_null(self):
        items = {item["id"]: item for item in self.get_data()["items"]}

        self.assertIsNone(items[self.pending.id]["attendance"])
        self.assertEqual(items[self.approved.id]["attendance"], "present")
        self.assertEqual(items[self.completed.id]["attendance"], "absent")
        self.assertIsNone(items[self.approved.id]["customer"]["phone"])

    def test_bookings_are_ordered_newest_first_with_id_tiebreaker(self):
        older = datetime(2029, 1, 1, tzinfo=timezone.utc)
        newer = older + timedelta(days=1)

        Booking.objects.filter(pk=self.pending.pk).update(created_at=older)
        Booking.objects.filter(pk__in=[self.approved.pk, self.completed.pk]).update(
            created_at=newer
        )

        self.assertEqual(
            self.get_ids(),
            [self.completed.id, self.approved.id, self.pending.id],
        )

    def test_status_filter(self):
        self.assertEqual(
            self.get_ids({"status": "approved"}),
            [self.approved.id],
        )

    def test_tour_filter(self):
        self.assertEqual(
            self.get_ids({"tour_id": self.other_tour.id}),
            [self.approved.id],
        )

    def test_departure_filter(self):
        self.assertEqual(
            self.get_ids({"departure_id": self.other_departure.id}),
            [self.approved.id],
        )

    def test_search_matches_customer_name_case_insensitively(self):
        self.assertEqual(
            set(self.get_ids({"search": "aRoHa"})),
            {self.pending.id, self.completed.id},
        )

    def test_search_matches_booking_reference_case_insensitively(self):
        self.assertEqual(
            self.get_ids({"search": "kt-admin02"}),
            [self.approved.id],
        )

    def test_blank_search_returns_all_bookings(self):
        self.assertEqual(self.get_data({"search": "   "})["total"], 3)

    def test_date_range_includes_both_boundary_dates(self):
        ids = self.get_ids({"date_from": "2030-06-10", "date_to": "2030-06-20"})

        self.assertEqual(
            set(ids),
            {self.pending.id, self.approved.id, self.completed.id},
        )

    def test_date_filters_work_independently(self):
        self.assertEqual(
            self.get_ids({"date_from": "2030-06-11"}),
            [self.approved.id],
        )
        self.assertEqual(
            set(self.get_ids({"date_to": "2030-06-10"})),
            {self.pending.id, self.completed.id},
        )

    def test_date_filter_uses_departure_date_not_booking_creation_date(self):
        Booking.objects.all().update(created_at=datetime(2029, 1, 1, tzinfo=timezone.utc))

        self.assertEqual(
            self.get_ids({"date_from": "2030-06-20", "date_to": "2030-06-20"}),
            [self.approved.id],
        )

    def test_date_filter_uses_utc_even_when_active_timezone_changes(self):
        from django.utils import timezone as django_timezone

        Departure.objects.filter(pk=self.other_departure.pk).update(
            start_datetime=datetime(2030, 6, 20, 23, 30, tzinfo=timezone.utc)
        )

        with django_timezone.override("Pacific/Auckland"):
            ids = self.get_ids({"date_from": "2030-06-20", "date_to": "2030-06-20"})

        self.assertEqual(ids, [self.approved.id])

    def test_filters_can_be_combined(self):
        params = {
            "status": "completed",
            "tour_id": self.tour.id,
            "departure_id": self.departure.id,
            "date_from": "2030-06-10",
            "date_to": "2030-06-10",
            "search": "Aroha",
        }

        self.assertEqual(self.get_ids(params), [self.completed.id])

    def test_no_matches_returns_empty_list(self):
        data = self.get_data({"search": "No matching customer"})

        self.assertEqual(data["items"], [])
        self.assertEqual(data["total"], 0)

    def test_invalid_filters_are_rejected(self):
        invalid_queries = [
            {"status": "unknown"},
            {"tour_id": "abc"},
            {"tour_id": "0"},
            {"departure_id": "-1"},
            {"date_from": "not-a-date"},
            {"date_to": "2030-02-30"},
            {"date_from": "2030-06-21", "date_to": "2030-06-20"},
        ]

        for params in invalid_queries:
            with self.subTest(params=params):
                response = self.client.get(self.url, params)
                self.assert_error(response, 422, "VALIDATION_ERROR")

    def test_pagination_returns_total_and_distinct_pages(self):
        first = self.get_data({"page": 1, "page_size": 2})
        second = self.get_data({"page": 2, "page_size": 2})

        self.assertEqual(first["total"], 3)
        self.assertEqual(first["page"], 1)
        self.assertEqual(first["page_size"], 2)
        self.assertEqual(len(first["items"]), 2)
        self.assertEqual(second["page"], 2)
        self.assertEqual(len(second["items"]), 1)

        first_ids = {item["id"] for item in first["items"]}
        second_ids = {item["id"] for item in second["items"]}
        self.assertFalse(first_ids & second_ids)

    def test_page_size_is_capped_at_fifty(self):
        data = self.get_data({"page_size": 100})

        self.assertEqual(data["page_size"], 50)

    def test_invalid_pagination_is_rejected(self):
        invalid_queries = [
            {"page": 0},
            {"page": "abc"},
            {"page": 999},
            {"page_size": 0},
            {"page_size": "abc"},
        ]

        for params in invalid_queries:
            with self.subTest(params=params):
                response = self.client.get(self.url, params)
                self.assert_error(response, 422, "VALIDATION_ERROR")
