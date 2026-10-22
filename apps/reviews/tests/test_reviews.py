"""Automated tests for customer and administrative review endpoints.
Tests public review listings customer submission guards and admin moderation.
Verifies name formatting booking completion checks and permission rules.
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import UserRole
from apps.bookings.models import Booking, BookingStatus
from apps.catalog.models import Category, Tour, TourStatus
from apps.departures.models import Departure, DepartureStatus
from apps.reviews.models import Review
from apps.reviews.services import format_reviewer_name

User = get_user_model()


class ReviewApiTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email="admin@kiwitrails.test",
            full_name="Admin User",
            role=UserRole.ADMIN,
        )
        self.customer1 = User.objects.create_user(
            email="aroha@kiwitrails.test",
            full_name="Aroha Smith",
            role=UserRole.CUSTOMER,
        )
        self.customer2 = User.objects.create_user(
            email="tane@kiwitrails.test",
            full_name="Tane",
            role=UserRole.CUSTOMER,
        )

        self.category = Category.objects.create(name="Scenic Walks")
        self.tour = Tour.objects.create(
            title="Taupo Lake Cruise",
            description="Scenic lake tour",
            location="Taupo",
            category=self.category,
            price_per_person=Decimal("150.00"),
            duration_days=1,
            itinerary="Cruise the lake",
            status=TourStatus.ACTIVE,
        )
        self.archived_tour = Tour.objects.create(
            title="Secret Forest",
            description="Hidden tracks",
            location="Rotorua",
            category=self.category,
            price_per_person=Decimal("80.00"),
            duration_days=1,
            itinerary="Forest walk",
            status=TourStatus.ARCHIVED,
        )

        now = timezone.now()
        self.departure = Departure.objects.create(
            tour=self.tour,
            start_datetime=now + timedelta(days=10),
            booking_deadline=now + timedelta(days=5),
            capacity=20,
            status=DepartureStatus.SCHEDULED,
        )
        self.completed_departure = Departure.objects.create(
            tour=self.tour,
            start_datetime=now - timedelta(days=10),
            booking_deadline=now - timedelta(days=15),
            capacity=20,
            status=DepartureStatus.COMPLETED,
        )

        self.booking_completed1 = Booking.objects.create(
            booking_reference="BK-TEST-001",
            user=self.customer1,
            departure=self.completed_departure,
            traveller_count=2,
            price_per_person=Decimal("150.00"),
            subtotal=Decimal("300.00"),
            total_price=Decimal("300.00"),
            status=BookingStatus.COMPLETED,
        )
        self.booking_completed2 = Booking.objects.create(
            booking_reference="BK-TEST-002",
            user=self.customer2,
            departure=self.completed_departure,
            traveller_count=1,
            price_per_person=Decimal("150.00"),
            subtotal=Decimal("150.00"),
            total_price=Decimal("150.00"),
            status=BookingStatus.COMPLETED,
        )
        self.booking_approved = Booking.objects.create(
            booking_reference="BK-TEST-003",
            user=self.customer1,
            departure=self.departure,
            traveller_count=2,
            price_per_person=Decimal("150.00"),
            subtotal=Decimal("300.00"),
            total_price=Decimal("300.00"),
            status=BookingStatus.APPROVED,
        )

        self.existing_review = Review.objects.create(
            booking=self.booking_completed1,
            user=self.customer1,
            tour=self.tour,
            rating=5,
            comment="Wonderful day on the lake.",
        )

    def test_format_reviewer_name_helper(self):
        self.assertEqual(format_reviewer_name(self.customer1), "Aroha S.")
        self.assertEqual(format_reviewer_name(self.customer2), "Tane")
        self.assertEqual(format_reviewer_name(None), "")

    def test_list_tour_reviews_public(self):
        response = self.client.get(f"/api/v1/tours/{self.tour.id}/reviews")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["total"], 1)
        item = data["items"][0]
        self.assertEqual(item["id"], self.existing_review.id)
        self.assertEqual(item["tour_id"], self.tour.id)
        self.assertEqual(item["booking_id"], self.booking_completed1.id)
        self.assertEqual(item["rating"], 5)
        self.assertEqual(item["comment"], "Wonderful day on the lake.")
        self.assertEqual(item["reviewer_name"], "Aroha S.")
        self.assertIn("created_at", item)

    def test_list_tour_reviews_not_found(self):
        response = self.client.get("/api/v1/tours/99999/reviews")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_tour_reviews_archived_tour_public(self):
        response = self.client.get(f"/api/v1/tours/{self.archived_tour.id}/reviews")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_tour_reviews_archived_tour_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f"/api/v1/tours/{self.archived_tour.id}/reviews")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_review_success(self):
        self.client.force_authenticate(user=self.customer2)
        payload = {
            "booking_id": self.booking_completed2.id,
            "rating": 4,
            "comment": "Great tour and scenic route.",
        }
        response = self.client.post("/api/v1/reviews", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["tour_id"], self.tour.id)
        self.assertEqual(data["booking_id"], self.booking_completed2.id)
        self.assertEqual(data["rating"], 4)
        self.assertEqual(data["comment"], "Great tour and scenic route.")
        self.assertEqual(data["reviewer_name"], "Tane")

    def test_create_review_without_comment(self):
        dep = Departure.objects.create(
            tour=self.tour,
            start_datetime=timezone.now() - timedelta(days=2),
            booking_deadline=timezone.now() - timedelta(days=4),
            capacity=10,
            status=DepartureStatus.COMPLETED,
        )
        bk = Booking.objects.create(
            booking_reference="BK-TEST-004",
            user=self.customer2,
            departure=dep,
            traveller_count=1,
            price_per_person=Decimal("150.00"),
            subtotal=Decimal("150.00"),
            total_price=Decimal("150.00"),
            status=BookingStatus.COMPLETED,
        )
        self.client.force_authenticate(user=self.customer2)
        payload = {"booking_id": bk.id, "rating": 3}
        response = self.client.post("/api/v1/reviews", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["comment"], "")

    def test_create_review_unauthenticated(self):
        response = self.client.post("/api/v1/reviews", {"booking_id": 1, "rating": 5})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_not_completed_booking(self):
        self.client.force_authenticate(user=self.customer1)
        payload = {"booking_id": self.booking_approved.id, "rating": 5}
        response = self.client.post("/api/v1/reviews", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"]["code"], "REVIEW_NOT_ALLOWED")

    def test_create_review_not_owner_booking(self):
        self.client.force_authenticate(user=self.customer1)
        payload = {"booking_id": self.booking_completed2.id, "rating": 5}
        response = self.client.post("/api/v1/reviews", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"]["code"], "REVIEW_NOT_ALLOWED")

    def test_create_review_non_existent_booking(self):
        self.client.force_authenticate(user=self.customer1)
        payload = {"booking_id": 99999, "rating": 5}
        response = self.client.post("/api/v1/reviews", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"]["code"], "REVIEW_NOT_ALLOWED")

    def test_create_review_already_reviewed(self):
        self.client.force_authenticate(user=self.customer1)
        payload = {"booking_id": self.booking_completed1.id, "rating": 4}
        response = self.client.post("/api/v1/reviews", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"]["code"], "REVIEW_NOT_ALLOWED")

    def test_create_review_validation_errors(self):
        self.client.force_authenticate(user=self.customer1)
        payload = {"booking_id": 0, "rating": 6, "comment": "x" * 1001}
        response = self.client.post("/api/v1/reviews", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        fields = response.data["error"]["fields"]
        self.assertIn("booking_id", fields)
        self.assertIn("rating", fields)
        self.assertIn("comment", fields)

    def test_list_admin_reviews_success(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/v1/admin/reviews")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["total"], 1)
        item = data["items"][0]
        self.assertEqual(item["tour_title"], "Taupo Lake Cruise")
        self.assertEqual(item["user_id"], self.customer1.id)
        self.assertEqual(item["reviewer_name"], "Aroha S.")

    def test_list_admin_reviews_filter_tour_id(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f"/api/v1/admin/reviews?tour_id={self.tour.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["total"], 1)

        response2 = self.client.get("/api/v1/admin/reviews?tour_id=99999")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data["data"]["total"], 0)

    def test_list_admin_reviews_filter_rating(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/v1/admin/reviews?rating=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["total"], 1)

        response2 = self.client.get("/api/v1/admin/reviews?rating=1")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data["data"]["total"], 0)

    def test_list_admin_reviews_filter_invalid(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/v1/admin/reviews?rating=9")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

        response2 = self.client.get("/api/v1/admin/reviews?tour_id=invalid")
        self.assertEqual(response2.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_list_admin_reviews_unauthenticated(self):
        response = self.client.get("/api/v1/admin/reviews")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_admin_reviews_forbidden_customer(self):
        self.client.force_authenticate(user=self.customer1)
        response = self.client.get("/api/v1/admin/reviews")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
