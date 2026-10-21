"""Automated tests for public catalog endpoints.
Tests tour listings details categories and guides.
Verifies single query performance and visibility rules for archived tours.
"""

from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.bookings.models import Booking, BookingStatus
from apps.catalog.models import (
    Category,
    Guide,
    Tour,
    TourFaq,
    TourImage,
    TourStatus,
)
from apps.core.testing import make_admin, make_client, make_customer
from apps.departures.models import Departure, DepartureStatus
from apps.departures.services import get_seats_taken
from apps.reviews.models import Review


class ToursPublicTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.water_cat = Category.objects.create(name="Water")
        self.culture_cat = Category.objects.create(name="Culture")
        self.adventure_cat = Category.objects.create(name="Adventure")

        self.guide = Guide.objects.create(
            full_name="Hemi Walker",
            bio="Local guide for 12 years.",
            photo_url="/media/seed/guides/hemi.jpg",
            languages="English, Te Reo Maori",
        )

        now = timezone.now()

        self.active_tour_1 = Tour.objects.create(
            title="Taupo Lake Cruise",
            description="A relaxed cruise on Lake Taupo.",
            location="Taupo",
            category=self.water_cat,
            price_per_person=Decimal("249.00"),
            duration_days=1,
            itinerary="9:00 Board at wharf.",
            accessibility_info="Wheelchair accessible.",
            visitor_guidelines="Warm clothes recommended.",
            meeting_point_name="Taupo Wharf",
            meeting_lat=Decimal("-38.685700"),
            meeting_lng=Decimal("176.070200"),
            guide=self.guide,
            cancellation_days=7,
            status=TourStatus.ACTIVE,
        )
        self.image_1 = TourImage.objects.create(
            tour=self.active_tour_1,
            image_url="/media/seed/lake-cruise.jpg",
            alt_text="Boat on lake",
            sort_order=1,
        )
        self.faq_1 = TourFaq.objects.create(
            tour=self.active_tour_1,
            question="Is lunch included?",
            answer="Yes a light lunch.",
            sort_order=1,
        )
        self.departure_1 = Departure.objects.create(
            tour=self.active_tour_1,
            start_datetime=now + timedelta(days=10),
            booking_deadline=now + timedelta(days=8),
            capacity=12,
            status=DepartureStatus.SCHEDULED,
        )

        self.customer = make_customer(email="customer@kiwitrails.test")
        self.booking_1 = Booking.objects.create(
            user=self.customer,
            departure=self.departure_1,
            booking_reference="KT-TEST01",
            traveller_count=2,
            price_per_person=Decimal("249.00"),
            subtotal=Decimal("498.00"),
            discount_amount=Decimal("0.00"),
            total_price=Decimal("498.00"),
            status=BookingStatus.COMPLETED,
        )
        Review.objects.create(
            booking=self.booking_1,
            user=self.customer,
            tour=self.active_tour_1,
            rating=5,
            comment="Wonderful tour.",
        )

        self.active_tour_2 = Tour.objects.create(
            title="Rotorua Cultural Village",
            description="Traditional Maori experience.",
            location="Rotorua",
            category=self.culture_cat,
            price_per_person=Decimal("120.00"),
            duration_days=1,
            itinerary="10:00 Welcome ceremony.",
            status=TourStatus.ACTIVE,
        )

        self.archived_tour = Tour.objects.create(
            title="Queenstown Old Jet",
            description="Retired speed boat trip.",
            location="Queenstown",
            category=self.adventure_cat,
            price_per_person=Decimal("350.00"),
            duration_days=1,
            itinerary="Old itinerary.",
            status=TourStatus.ARCHIVED,
        )

        self.admin = make_admin(email="admin@kiwitrails.test")

    def test_list_tours_success(self):
        response = self.client.get("/api/v1/tours")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["total"], 2)
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["page_size"], 10)
        items = data["items"]
        self.assertEqual(len(items), 2)

        titles = [item["title"] for item in items]
        self.assertIn("Taupo Lake Cruise", titles)
        self.assertIn("Rotorua Cultural Village", titles)
        self.assertNotIn("Queenstown Old Jet", titles)

        item = next(i for i in items if i["id"] == self.active_tour_1.id)
        self.assertEqual(item["location"], "Taupo")
        self.assertEqual(item["category_id"], self.water_cat.id)
        self.assertEqual(item["category"], "Water")
        self.assertEqual(float(item["price_per_person"]), 249.00)
        self.assertEqual(item["duration_days"], 1)
        self.assertEqual(item["image_url"], "/media/seed/lake-cruise.jpg")
        self.assertEqual(item["average_rating"], 5.0)
        self.assertEqual(item["review_count"], 1)
        self.assertIsNotNone(item["next_departure"])
        self.assertEqual(item["seats_left"], 10)
        self.assertEqual(item["status"], "active")

    def test_list_tours_filters(self):
        res_search = self.client.get("/api/v1/tours", {"search": "cruise"})
        self.assertEqual(res_search.data["data"]["total"], 1)
        self.assertEqual(res_search.data["data"]["items"][0]["title"], "Taupo Lake Cruise")

        res_loc = self.client.get("/api/v1/tours", {"location": "Rotorua"})
        self.assertEqual(res_loc.data["data"]["total"], 1)
        self.assertEqual(res_loc.data["data"]["items"][0]["title"], "Rotorua Cultural Village")

        res_cat = self.client.get("/api/v1/tours", {"category_id": self.water_cat.id})
        self.assertEqual(res_cat.data["data"]["total"], 1)
        self.assertEqual(res_cat.data["data"]["items"][0]["title"], "Taupo Lake Cruise")

        res_price = self.client.get("/api/v1/tours", {"min_price": "200", "max_price": "300"})
        self.assertEqual(res_price.data["data"]["total"], 1)
        self.assertEqual(res_price.data["data"]["items"][0]["title"], "Taupo Lake Cruise")

        res_sort = self.client.get("/api/v1/tours", {"sort": "price_asc"})
        items = res_sort.data["data"]["items"]
        self.assertEqual(items[0]["title"], "Rotorua Cultural Village")
        self.assertEqual(items[1]["title"], "Taupo Lake Cruise")

        res_sort_desc = self.client.get("/api/v1/tours", {"sort": "price_desc"})
        items_desc = res_sort_desc.data["data"]["items"]
        self.assertEqual(items_desc[0]["title"], "Taupo Lake Cruise")
        self.assertEqual(items_desc[1]["title"], "Rotorua Cultural Village")

    def test_list_tours_bad_sort(self):
        response = self.client.get("/api/v1/tours", {"sort": "invalid_sort"})
        self.assertEqual(response.status_code, 422)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")
        self.assertIn("sort", response.data["error"]["fields"])

    def test_list_tours_num_queries(self):
        for i in range(5):
            Tour.objects.create(
                title=f"Sample Tour {i}",
                description=f"Sample Description {i}",
                location="Auckland",
                category=self.adventure_cat,
                price_per_person=Decimal("99.00"),
                duration_days=1,
                itinerary="Walk around.",
                status=TourStatus.ACTIVE,
            )

        with self.assertNumQueries(2):
            response = self.client.get("/api/v1/tours")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["data"]["total"], 7)

    def test_get_tour_detail_success(self):
        response = self.client.get(f"/api/v1/tours/{self.active_tour_1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["id"], self.active_tour_1.id)
        self.assertEqual(data["title"], "Taupo Lake Cruise")
        self.assertEqual(data["description"], "A relaxed cruise on Lake Taupo.")
        self.assertEqual(data["location"], "Taupo")
        self.assertEqual(data["category_id"], self.water_cat.id)
        self.assertEqual(data["category"], "Water")
        self.assertEqual(float(data["price_per_person"]), 249.00)
        self.assertEqual(data["duration_days"], 1)
        self.assertEqual(data["itinerary"], "9:00 Board at wharf.")
        self.assertEqual(data["accessibility_info"], "Wheelchair accessible.")
        self.assertEqual(data["visitor_guidelines"], "Warm clothes recommended.")
        self.assertEqual(
            data["meeting_point"],
            {"name": "Taupo Wharf", "lat": -38.6857, "lng": 176.0702},
        )
        self.assertEqual(data["cancellation_days"], 7)
        self.assertEqual(data["status"], "active")
        self.assertEqual(len(data["images"]), 1)
        self.assertEqual(data["images"][0]["image_url"], "/media/seed/lake-cruise.jpg")
        self.assertEqual(data["guide"]["id"], self.guide.id)
        self.assertEqual(data["guide"]["full_name"], "Hemi Walker")
        self.assertEqual(data["guide"]["languages"], ["English", "Te Reo Maori"])
        self.assertEqual(len(data["faqs"]), 1)
        self.assertEqual(data["faqs"][0]["question"], "Is lunch included?")
        self.assertEqual(data["average_rating"], 5.0)
        self.assertEqual(data["review_count"], 1)
        self.assertEqual(len(data["departures"]), 1)
        dep = data["departures"][0]
        self.assertEqual(dep["id"], self.departure_1.id)
        self.assertEqual(dep["capacity"], 12)
        seats_taken = get_seats_taken(self.departure_1)
        self.assertEqual(dep["seats_taken"], seats_taken)
        self.assertEqual(dep["seats_left"], max(0, self.departure_1.capacity - seats_taken))
        self.assertTrue(dep["booking_open"])

    def test_get_tour_detail_archived_hidden_from_public(self):
        anon_res = self.client.get(f"/api/v1/tours/{self.archived_tour.id}")
        self.assertEqual(anon_res.status_code, 404)
        self.assertEqual(anon_res.data["error"]["code"], "NOT_FOUND")

        cust_client = make_client(self.customer)
        cust_res = cust_client.get(f"/api/v1/tours/{self.archived_tour.id}")
        self.assertEqual(cust_res.status_code, 404)
        self.assertEqual(cust_res.data["error"]["code"], "NOT_FOUND")

    def test_get_tour_detail_archived_visible_to_admin(self):
        admin_client = make_client(self.admin)
        response = admin_client.get(f"/api/v1/tours/{self.archived_tour.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["id"], self.archived_tour.id)
        self.assertEqual(response.data["data"]["status"], "archived")

    def test_get_tour_detail_not_found(self):
        response = self.client.get("/api/v1/tours/999999")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "NOT_FOUND")

    def test_list_categories(self):
        response = self.client.get("/api/v1/categories")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        items = response.data["data"]["items"]
        self.assertEqual(len(items), 3)
        names = [item["name"] for item in items]
        self.assertEqual(names, ["Adventure", "Culture", "Water"])

    def test_get_guide_detail(self):
        response = self.client.get(f"/api/v1/guides/{self.guide.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["id"], self.guide.id)
        self.assertEqual(data["full_name"], "Hemi Walker")
        self.assertEqual(data["bio"], "Local guide for 12 years.")
        self.assertEqual(data["photo_url"], "/media/seed/guides/hemi.jpg")
        self.assertEqual(data["languages"], ["English", "Te Reo Maori"])

    def test_get_guide_not_found(self):
        response = self.client.get("/api/v1/guides/999999")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "NOT_FOUND")
