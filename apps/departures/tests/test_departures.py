"""Automated tests for public and admin departure endpoints.
Tests departure listings calendar schedules creation and capacity updates.
Verifies status transitions cascading completions and conflict handling.
"""

from datetime import datetime, timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.bookings.models import Booking, BookingStatus
from apps.catalog.models import Category, Tour, TourStatus
from apps.core.testing import make_admin, make_client, make_customer
from apps.departures.models import Departure, DepartureStatus


class DeparturesTests(TestCase):
    def setUp(self):
        self.anon_client = APIClient()
        self.admin = make_admin(email="admin@kiwitrails.test")
        self.admin_client = make_client(self.admin)
        self.customer = make_customer(email="customer@kiwitrails.test")
        self.customer_client = make_client(self.customer)

        self.category = Category.objects.create(name="Water")
        self.active_tour = Tour.objects.create(
            title="Taupō Lake Cruise",
            description="Lake cruise.",
            location="Taupō",
            category=self.category,
            price_per_person=Decimal("249.00"),
            duration_days=1,
            itinerary="Boarding at wharf.",
            status=TourStatus.ACTIVE,
        )
        self.archived_tour = Tour.objects.create(
            title="Old Jet Boat",
            description="Old tour.",
            location="Queenstown",
            category=self.category,
            price_per_person=Decimal("150.00"),
            duration_days=1,
            itinerary="Old itinerary.",
            status=TourStatus.ARCHIVED,
        )

        now = timezone.now()
        self.dep1 = Departure.objects.create(
            tour=self.active_tour,
            start_datetime=now + timedelta(days=10),
            booking_deadline=now + timedelta(days=8),
            capacity=12,
            status=DepartureStatus.SCHEDULED,
        )
        self.dep2 = Departure.objects.create(
            tour=self.active_tour,
            start_datetime=now + timedelta(days=20),
            booking_deadline=now + timedelta(days=18),
            capacity=10,
            status=DepartureStatus.SCHEDULED,
        )
        self.cancelled_dep = Departure.objects.create(
            tour=self.active_tour,
            start_datetime=now + timedelta(days=15),
            booking_deadline=now + timedelta(days=13),
            capacity=8,
            status=DepartureStatus.CANCELLED,
        )
        self.past_dep = Departure.objects.create(
            tour=self.active_tour,
            start_datetime=now - timedelta(days=5),
            booking_deadline=now - timedelta(days=7),
            capacity=10,
            status=DepartureStatus.SCHEDULED,
        )

    def test_list_tour_departures_success(self):
        response = self.anon_client.get(f"/api/v1/tours/{self.active_tour.id}/departures")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        items = response.data["data"]["items"]
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["id"], self.dep1.id)
        self.assertEqual(items[1]["id"], self.dep2.id)
        self.assertEqual(items[0]["capacity"], 12)
        self.assertEqual(items[0]["seats_taken"], 0)
        self.assertEqual(items[0]["seats_left"], 12)
        self.assertTrue(items[0]["booking_open"])
        self.assertEqual(items[0]["status"], "scheduled")

    def test_list_tour_departures_not_found(self):
        response = self.anon_client.get("/api/v1/tours/999999/departures")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"]["code"], "NOT_FOUND")

    def test_list_tour_departures_archived_hidden_from_public(self):
        now = timezone.now()
        Departure.objects.create(
            tour=self.archived_tour,
            start_datetime=now + timedelta(days=10),
            booking_deadline=now + timedelta(days=8),
            capacity=10,
            status=DepartureStatus.SCHEDULED,
        )
        response = self.anon_client.get(f"/api/v1/tours/{self.archived_tour.id}/departures")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        admin_response = self.admin_client.get(f"/api/v1/tours/{self.archived_tour.id}/departures")
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)

    def test_get_calendar_success(self):
        dec_time = timezone.make_aware(datetime(2026, 12, 10, 10, 0, 0))
        dec_deadline = timezone.make_aware(datetime(2026, 12, 8, 10, 0, 0))
        dec_dep = Departure.objects.create(
            tour=self.active_tour,
            start_datetime=dec_time,
            booking_deadline=dec_deadline,
            capacity=14,
            status=DepartureStatus.SCHEDULED,
        )
        Departure.objects.create(
            tour=self.active_tour,
            start_datetime=dec_time + timedelta(days=1),
            booking_deadline=dec_deadline,
            capacity=10,
            status=DepartureStatus.CANCELLED,
        )

        response = self.anon_client.get("/api/v1/departures/calendar?month=2026-12")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["month"], "2026-12")
        items = data["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], dec_dep.id)
        self.assertEqual(items[0]["tour_title"], "Taupō Lake Cruise")
        self.assertEqual(items[0]["capacity"], 14)

    def test_get_calendar_missing_month(self):
        response = self.anon_client.get("/api/v1/departures/calendar")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")
        self.assertIn("month", response.data["error"]["fields"])

    def test_get_calendar_invalid_month(self):
        response = self.anon_client.get("/api/v1/departures/calendar?month=2026-13")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")
        self.assertIn("month", response.data["error"]["fields"])

        res2 = self.anon_client.get("/api/v1/departures/calendar?month=invalid")
        self.assertEqual(res2.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_create_departure_success(self):
        future_start = timezone.now() + timedelta(days=30)
        future_deadline = future_start - timedelta(days=2)
        payload = {
            "start_datetime": future_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "capacity": 15,
            "booking_deadline": future_deadline.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        response = self.admin_client.post(
            f"/api/v1/admin/tours/{self.active_tour.id}/departures",
            payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["tour_id"], self.active_tour.id)
        self.assertEqual(data["capacity"], 15)
        self.assertEqual(data["seats_taken"], 0)
        self.assertEqual(data["seats_left"], 15)
        self.assertTrue(data["booking_open"])
        self.assertEqual(data["status"], "scheduled")

    def test_create_departure_validation_errors(self):
        past_start = timezone.now() - timedelta(days=1)
        future_deadline = timezone.now() + timedelta(days=2)
        payload = {
            "start_datetime": past_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "capacity": 0,
            "booking_deadline": future_deadline.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        response = self.admin_client.post(
            f"/api/v1/admin/tours/{self.active_tour.id}/departures",
            payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")
        fields = response.data["error"]["fields"]
        self.assertIn("capacity", fields)
        self.assertIn("start_datetime", fields)

    def test_create_departure_deadline_after_start(self):
        future_start = timezone.now() + timedelta(days=10)
        invalid_deadline = future_start + timedelta(days=1)
        payload = {
            "start_datetime": future_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "capacity": 10,
            "booking_deadline": invalid_deadline.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        response = self.admin_client.post(
            f"/api/v1/admin/tours/{self.active_tour.id}/departures",
            payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("booking_deadline", response.data["error"]["fields"])

    def test_create_departure_not_found(self):
        future_start = timezone.now() + timedelta(days=10)
        future_deadline = future_start - timedelta(days=2)
        payload = {
            "start_datetime": future_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "capacity": 10,
            "booking_deadline": future_deadline.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        response = self.admin_client.post(
            "/api/v1/admin/tours/999999/departures", payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_departure_unauthenticated(self):
        response = self.anon_client.post(
            f"/api/v1/admin/tours/{self.active_tour.id}/departures", {}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_departure_forbidden_customer(self):
        response = self.customer_client.post(
            f"/api/v1/admin/tours/{self.active_tour.id}/departures", {}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_departure_success(self):
        response = self.admin_client.put(
            f"/api/v1/admin/departures/{self.dep1.id}",
            {"capacity": 16},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["capacity"], 16)
        self.dep1.refresh_from_db()
        self.assertEqual(self.dep1.capacity, 16)

    def test_update_departure_capacity_conflict(self):
        Booking.objects.create(
            user=self.customer,
            departure=self.dep1,
            booking_reference="KT-TEST99",
            traveller_count=6,
            price_per_person=Decimal("249.00"),
            subtotal=Decimal("1494.00"),
            discount_amount=Decimal("0.00"),
            total_price=Decimal("1494.00"),
            status=BookingStatus.APPROVED,
        )
        response = self.admin_client.put(
            f"/api/v1/admin/departures/{self.dep1.id}",
            {"capacity": 4},
            format="json",
        )
        self.assertEqual(response.status_code, 409)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "CAPACITY_CONFLICT")
        self.assertEqual(
            response.data["error"]["message"],
            "Capacity cannot be lower than the 6 seats already taken.",
        )
        self.assertEqual(
            response.data["error"]["fields"],
            {"capacity": "Must be at least 6."},
        )

    def test_update_departure_not_found(self):
        response = self.admin_client.put(
            "/api/v1/admin/departures/999999", {"capacity": 10}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_departure_unauthenticated(self):
        response = self.anon_client.put(
            f"/api/v1/admin/departures/{self.dep1.id}", {}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_departure_forbidden_customer(self):
        response = self.customer_client.put(
            f"/api/v1/admin/departures/{self.dep1.id}", {}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_set_departure_status_completed_cascades_bookings(self):
        booking_app = Booking.objects.create(
            user=self.customer,
            departure=self.dep1,
            booking_reference="KT-APP01",
            traveller_count=2,
            price_per_person=Decimal("249.00"),
            subtotal=Decimal("498.00"),
            discount_amount=Decimal("0.00"),
            total_price=Decimal("498.00"),
            status=BookingStatus.APPROVED,
        )
        booking_pend = Booking.objects.create(
            user=self.customer,
            departure=self.dep1,
            booking_reference="KT-PEND01",
            traveller_count=1,
            price_per_person=Decimal("249.00"),
            subtotal=Decimal("249.00"),
            discount_amount=Decimal("0.00"),
            total_price=Decimal("249.00"),
            status=BookingStatus.PENDING,
        )

        response = self.admin_client.patch(
            f"/api/v1/admin/departures/{self.dep1.id}/status",
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["status"], "completed")
        self.assertFalse(data["booking_open"])

        self.dep1.refresh_from_db()
        self.assertEqual(self.dep1.status, DepartureStatus.COMPLETED)

        booking_app.refresh_from_db()
        self.assertEqual(booking_app.status, BookingStatus.COMPLETED)

        booking_pend.refresh_from_db()
        self.assertEqual(booking_pend.status, BookingStatus.PENDING)

    def test_set_departure_status_cancelled(self):
        booking = Booking.objects.create(
            user=self.customer,
            departure=self.dep1,
            booking_reference="KT-APP02",
            traveller_count=2,
            price_per_person=Decimal("249.00"),
            subtotal=Decimal("498.00"),
            discount_amount=Decimal("0.00"),
            total_price=Decimal("498.00"),
            status=BookingStatus.APPROVED,
        )

        response = self.admin_client.patch(
            f"/api/v1/admin/departures/{self.dep1.id}/status",
            {"status": "cancelled"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["status"], "cancelled")

        booking.refresh_from_db()
        self.assertEqual(booking.status, BookingStatus.APPROVED)

    def test_set_departure_status_invalid(self):
        response = self.admin_client.patch(
            f"/api/v1/admin/departures/{self.dep1.id}/status",
            {"status": "scheduled"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")

    def test_set_departure_status_not_found(self):
        response = self.admin_client.patch(
            "/api/v1/admin/departures/999999/status",
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_set_departure_status_unauthenticated(self):
        response = self.anon_client.patch(
            f"/api/v1/admin/departures/{self.dep1.id}/status",
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_set_departure_status_forbidden_customer(self):
        response = self.customer_client.patch(
            f"/api/v1/admin/departures/{self.dep1.id}/status",
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
