"""Tests for Trip Match quiz evaluation and scoring API."""

from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.catalog.models import Category, Tour, TourStatus
from apps.departures.models import Departure, DepartureStatus
from apps.matching.services import match_tours


class TripMatchApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.water_cat = Category.objects.create(name="Water")
        self.hiking_cat = Category.objects.create(name="Hiking")

        self.taupo = Tour.objects.create(
            title="Taupō Lake Cruise",
            description="Scenic lake cruise with rock carvings.",
            location="Taupō",
            category=self.water_cat,
            price_per_person=Decimal("249.00"),
            duration_days=1,
            itinerary="Cruise across the lake to rock carvings.",
            accessibility_info="Wheelchair access on the main deck.",
            visitor_guidelines="Bring sun protection.",
            cancellation_days=7,
            operator_name="Taupō Moana Heritage Journeys",
            operator_story="Authentic local watermen history.",
            maori_led=True,
            operator_verified=True,
            status=TourStatus.ACTIVE,
        )

        self.tongariro = Tour.objects.create(
            title="Tongariro Alpine Crossing",
            description="Alpine day hike over volcanic terrain.",
            location="Tongariro",
            category=self.hiking_cat,
            price_per_person=Decimal("185.00"),
            duration_days=1,
            itinerary="Full day trek through craters.",
            accessibility_info="",
            visitor_guidelines="Warm layers required.",
            cancellation_days=7,
            operator_name="Alpine Guides Ltd",
            maori_led=False,
            operator_verified=False,
            status=TourStatus.ACTIVE,
        )

        now = timezone.now()
        # Add future scheduled departure for Taupo in December 2026
        target_dt = now.replace(year=2026, month=12, day=5, hour=9, minute=0, second=0)
        Departure.objects.create(
            tour=self.taupo,
            start_datetime=target_dt,
            booking_deadline=target_dt - timedelta(days=2),
            capacity=10,
            status=DepartureStatus.SCHEDULED,
        )

    def test_post_match_success(self):
        payload = {
            "interests": ["Water"],
            "budget_per_person": 300,
            "max_days": 2,
            "travellers": 3,
            "accessibility_needs": True,
            "month": "2026-12",
        }
        res = self.client.post("/api/v1/matches", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data.get("success"))
        items = res.data["data"]["items"]
        self.assertGreater(len(items), 0)

        top_match = items[0]
        self.assertEqual(top_match["tour_id"], self.taupo.id)
        self.assertEqual(top_match["title"], "Taupō Lake Cruise")
        self.assertTrue(top_match["maori_led"])
        self.assertEqual(top_match["operator_name"], "Taupō Moana Heritage Journeys")

        # Verify reasons are explainable
        reasons_text = " ".join(top_match["reasons"])
        self.assertIn("Matches your interest: Water", reasons_text)
        self.assertIn("Within budget", reasons_text)
        self.assertIn("Wheelchair access on the main deck", reasons_text)
        self.assertIn("Seats for 3 travellers", reasons_text)

    def test_post_match_with_trailing_slash(self):
        payload = {"interests": ["Water"]}
        res = self.client.post("/api/v1/matches/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_prefer_maori_led_prioritization(self):
        criteria = {
            "interests": ["Water", "Hiking"],
            "prefer_maori_led": True,
        }
        matches = match_tours(criteria)
        self.assertGreater(len(matches), 0)
        self.assertTrue(matches[0]["maori_led"])
        self.assertIn("Verified Māori led experience", " ".join(matches[0]["reasons"]))

    def test_invalid_month_format_rejected(self):
        payload = {"month": "invalid-month"}
        res = self.client.post("/api/v1/matches", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_negative_budget_rejected(self):
        payload = {"budget_per_person": -50}
        res = self.client.post("/api/v1/matches", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
