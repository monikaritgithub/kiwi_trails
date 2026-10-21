"""Automated tests for administrative catalog endpoints.
Tests admin tour management status changes image uploads and faqs.
Verifies role authorization validation rules and storage operations.
"""

import shutil
import tempfile
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.catalog.models import (
    Category,
    Guide,
    Tour,
    TourFaq,
    TourImage,
    TourStatus,
)
from apps.core.testing import make_admin, make_client, make_customer

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ToursAdminTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.admin = make_admin(email="admin@kiwitrails.test")
        self.admin_client = make_client(self.admin)
        self.customer = make_customer(email="customer@kiwitrails.test")
        self.customer_client = make_client(self.customer)
        self.anon_client = APIClient()

        self.water_cat = Category.objects.create(name="Water")
        self.culture_cat = Category.objects.create(name="Culture")

        self.guide = Guide.objects.create(
            full_name="Hemi Walker",
            bio="Local guide for 12 years.",
            photo_url="/media/seed/guides/hemi.jpg",
            languages="English, Te Reo Maori",
        )

        self.active_tour = Tour.objects.create(
            title="Taupo Lake Cruise",
            description="Relaxed lake cruise.",
            location="Taupo",
            category=self.water_cat,
            price_per_person=Decimal("249.00"),
            duration_days=1,
            itinerary="9:00 Boarding.",
            status=TourStatus.ACTIVE,
        )

        self.archived_tour = Tour.objects.create(
            title="Queenstown Old Jet",
            description="Retired speed boat trip.",
            location="Queenstown",
            category=self.water_cat,
            price_per_person=Decimal("350.00"),
            duration_days=1,
            itinerary="Old itinerary.",
            status=TourStatus.ARCHIVED,
        )

    def test_list_admin_tours_success(self):
        response = self.admin_client.get("/api/v1/admin/tours")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["total"], 2)
        titles = [item["title"] for item in data["items"]]
        self.assertIn("Taupo Lake Cruise", titles)
        self.assertIn("Queenstown Old Jet", titles)

    def test_list_admin_tours_filter_status(self):
        res_archived = self.admin_client.get("/api/v1/admin/tours", {"status": "archived"})
        self.assertEqual(res_archived.status_code, status.HTTP_200_OK)
        self.assertEqual(res_archived.data["data"]["total"], 1)
        self.assertEqual(res_archived.data["data"]["items"][0]["title"], "Queenstown Old Jet")

        res_active = self.admin_client.get("/api/v1/admin/tours", {"status": "active"})
        self.assertEqual(res_active.status_code, status.HTTP_200_OK)
        self.assertEqual(res_active.data["data"]["total"], 1)
        self.assertEqual(res_active.data["data"]["items"][0]["title"], "Taupo Lake Cruise")

    def test_list_admin_tours_filter_search(self):
        response = self.admin_client.get("/api/v1/admin/tours", {"search": "Queenstown"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["total"], 1)
        self.assertEqual(response.data["data"]["items"][0]["title"], "Queenstown Old Jet")

    def test_list_admin_tours_invalid_status(self):
        response = self.admin_client.get("/api/v1/admin/tours", {"status": "unknown"})
        self.assertEqual(response.status_code, 422)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")
        self.assertIn("status", response.data["error"]["fields"])

    def test_list_admin_tours_unauthenticated(self):
        response = self.anon_client.get("/api/v1/admin/tours")
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "UNAUTHENTICATED")

    def test_list_admin_tours_forbidden_customer(self):
        response = self.customer_client.get("/api/v1/admin/tours")
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "FORBIDDEN")

    def test_create_tour_success(self):
        payload = {
            "title": "Waitomo Glowworm Caves",
            "description": "Float through caves.",
            "location": "Waitomo",
            "category_id": self.water_cat.id,
            "price_per_person": 129.00,
            "duration_days": 1,
            "itinerary": "10:00 Meet visitor centre.",
            "meeting_point_name": "Waitomo Visitor Centre",
            "meeting_lat": -38.2608,
            "meeting_lng": 175.1035,
            "guide_id": self.guide.id,
        }
        response = self.admin_client.post("/api/v1/admin/tours", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["title"], "Waitomo Glowworm Caves")
        self.assertEqual(data["category_id"], self.water_cat.id)
        self.assertEqual(data["category"], "Water")
        self.assertEqual(float(data["price_per_person"]), 129.00)
        self.assertEqual(data["cancellation_days"], 7)
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["guide"]["id"], self.guide.id)
        self.assertEqual(data["meeting_point"]["name"], "Waitomo Visitor Centre")
        self.assertEqual(data["meeting_point"]["lat"], -38.2608)
        self.assertEqual(data["meeting_point"]["lng"], 175.1035)

    def test_create_tour_validation_errors(self):
        payload = {
            "title": "Invalid Tour",
            "description": "Desc",
            "location": "Taupo",
            "category_id": 99999,
            "price_per_person": -10.00,
            "duration_days": 0,
            "itinerary": "Itin",
            "meeting_lat": 95.0,
            "meeting_lng": 200.0,
        }
        response = self.admin_client.post("/api/v1/admin/tours", payload, format="json")
        self.assertEqual(response.status_code, 422)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")
        fields = response.data["error"]["fields"]
        self.assertIn("category_id", fields)
        self.assertIn("price_per_person", fields)
        self.assertIn("duration_days", fields)
        self.assertIn("meeting_lat", fields)
        self.assertIn("meeting_lng", fields)

    def test_create_tour_unauthenticated(self):
        response = self.anon_client.post("/api/v1/admin/tours", {}, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["error"]["code"], "UNAUTHENTICATED")

    def test_create_tour_forbidden_customer(self):
        response = self.customer_client.post("/api/v1/admin/tours", {}, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["error"]["code"], "FORBIDDEN")

    def test_update_tour_success(self):
        payload = {"price_per_person": 139.00, "cancellation_days": 5}
        response = self.admin_client.put(
            f"/api/v1/admin/tours/{self.active_tour.id}", payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(float(data["price_per_person"]), 139.00)
        self.assertEqual(data["cancellation_days"], 5)
        self.assertEqual(data["title"], "Taupo Lake Cruise")

    def test_update_tour_not_found(self):
        response = self.admin_client.put(
            "/api/v1/admin/tours/999999", {"price_per_person": 100.00}, format="json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["error"]["code"], "NOT_FOUND")

    def test_update_tour_validation_error(self):
        response = self.admin_client.put(
            f"/api/v1/admin/tours/{self.active_tour.id}",
            {"price_per_person": -50.00},
            format="json",
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")

    def test_update_tour_unauthenticated(self):
        response = self.anon_client.put(
            f"/api/v1/admin/tours/{self.active_tour.id}", {}, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_update_tour_forbidden_customer(self):
        response = self.customer_client.put(
            f"/api/v1/admin/tours/{self.active_tour.id}", {}, format="json"
        )
        self.assertEqual(response.status_code, 403)

    def test_set_tour_status_success(self):
        response = self.admin_client.patch(
            f"/api/v1/admin/tours/{self.active_tour.id}/status",
            {"status": "archived"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(
            response.data["data"],
            {"id": self.active_tour.id, "status": "archived"},
        )
        self.active_tour.refresh_from_db()
        self.assertEqual(self.active_tour.status, TourStatus.ARCHIVED)

    def test_set_tour_status_invalid(self):
        response = self.admin_client.patch(
            f"/api/v1/admin/tours/{self.active_tour.id}/status",
            {"status": "invalid_status"},
            format="json",
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")

    def test_set_tour_status_not_found(self):
        response = self.admin_client.patch(
            "/api/v1/admin/tours/999999/status",
            {"status": "archived"},
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    def test_set_tour_status_unauthenticated(self):
        response = self.anon_client.patch(
            f"/api/v1/admin/tours/{self.active_tour.id}/status",
            {"status": "archived"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_set_tour_status_forbidden_customer(self):
        response = self.customer_client.patch(
            f"/api/v1/admin/tours/{self.active_tour.id}/status",
            {"status": "archived"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_add_tour_image_success(self):
        fake_file = SimpleUploadedFile(
            "lake-cruise.jpg", b"fakeimagebytes", content_type="image/jpeg"
        )
        response = self.admin_client.post(
            f"/api/v1/admin/tours/{self.active_tour.id}/images",
            {"image": fake_file, "alt_text": "Boat on Lake Taupo", "sort_order": 0},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["alt_text"], "Boat on Lake Taupo")
        self.assertEqual(data["sort_order"], 0)
        self.assertTrue(data["image_url"].startswith("/media/tours/lake-cruise"))

    def test_add_tour_image_invalid_type(self):
        fake_file = SimpleUploadedFile("report.pdf", b"pdfbytes", content_type="application/pdf")
        response = self.admin_client.post(
            f"/api/v1/admin/tours/{self.active_tour.id}/images",
            {"image": fake_file},
            format="multipart",
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")
        self.assertIn("image", response.data["error"]["fields"])

    def test_add_tour_image_not_found(self):
        fake_file = SimpleUploadedFile("photo.jpg", b"bytes", content_type="image/jpeg")
        response = self.admin_client.post(
            "/api/v1/admin/tours/999999/images",
            {"image": fake_file},
            format="multipart",
        )
        self.assertEqual(response.status_code, 404)

    def test_add_tour_image_unauthenticated(self):
        fake_file = SimpleUploadedFile("photo.jpg", b"bytes", content_type="image/jpeg")
        response = self.anon_client.post(
            f"/api/v1/admin/tours/{self.active_tour.id}/images",
            {"image": fake_file},
            format="multipart",
        )
        self.assertEqual(response.status_code, 401)

    def test_add_tour_image_forbidden_customer(self):
        fake_file = SimpleUploadedFile("photo.jpg", b"bytes", content_type="image/jpeg")
        response = self.customer_client.post(
            f"/api/v1/admin/tours/{self.active_tour.id}/images",
            {"image": fake_file},
            format="multipart",
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_tour_image_success(self):
        image = TourImage.objects.create(
            tour=self.active_tour,
            image_url="/media/tours/temp.jpg",
            alt_text="Alt",
            sort_order=1,
        )
        response = self.admin_client.delete(f"/api/v1/admin/tour-images/{image.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"], {"deleted": True})
        self.assertFalse(TourImage.objects.filter(id=image.id).exists())

    def test_delete_tour_image_not_found(self):
        response = self.admin_client.delete("/api/v1/admin/tour-images/999999")
        self.assertEqual(response.status_code, 404)

    def test_delete_tour_image_unauthenticated(self):
        response = self.anon_client.delete("/api/v1/admin/tour-images/1")
        self.assertEqual(response.status_code, 401)

    def test_delete_tour_image_forbidden_customer(self):
        response = self.customer_client.delete("/api/v1/admin/tour-images/1")
        self.assertEqual(response.status_code, 403)

    def test_create_faq_success(self):
        payload = {
            "question": "Is lunch included?",
            "answer": "Yes, a light lunch.",
            "sort_order": 1,
        }
        response = self.admin_client.post(
            f"/api/v1/admin/tours/{self.active_tour.id}/faqs", payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["question"], "Is lunch included?")
        self.assertEqual(data["answer"], "Yes, a light lunch.")
        self.assertEqual(data["sort_order"], 1)

    def test_create_faq_validation_error(self):
        payload = {"answer": "Only answer without question."}
        response = self.admin_client.post(
            f"/api/v1/admin/tours/{self.active_tour.id}/faqs", payload, format="json"
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")
        self.assertIn("question", response.data["error"]["fields"])

    def test_create_faq_not_found(self):
        response = self.admin_client.post(
            "/api/v1/admin/tours/999999/faqs",
            {"question": "Q?", "answer": "A."},
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    def test_create_faq_unauthenticated(self):
        response = self.anon_client.post(
            f"/api/v1/admin/tours/{self.active_tour.id}/faqs", {}, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_create_faq_forbidden_customer(self):
        response = self.customer_client.post(
            f"/api/v1/admin/tours/{self.active_tour.id}/faqs", {}, format="json"
        )
        self.assertEqual(response.status_code, 403)

    def test_update_faq_success(self):
        faq = TourFaq.objects.create(
            tour=self.active_tour,
            question="Is lunch included?",
            answer="Yes, a light lunch.",
            sort_order=1,
        )
        payload = {"answer": "Yes, a light lunch and a hot drink."}
        response = self.admin_client.put(f"/api/v1/admin/faqs/{faq.id}", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["answer"], "Yes, a light lunch and a hot drink.")
        self.assertEqual(response.data["data"]["question"], "Is lunch included?")

    def test_update_faq_not_found(self):
        response = self.admin_client.put(
            "/api/v1/admin/faqs/999999", {"answer": "Updated"}, format="json"
        )
        self.assertEqual(response.status_code, 404)

    def test_update_faq_unauthenticated(self):
        response = self.anon_client.put("/api/v1/admin/faqs/1", {}, format="json")
        self.assertEqual(response.status_code, 401)

    def test_update_faq_forbidden_customer(self):
        response = self.customer_client.put("/api/v1/admin/faqs/1", {}, format="json")
        self.assertEqual(response.status_code, 403)

    def test_delete_faq_success(self):
        faq = TourFaq.objects.create(
            tour=self.active_tour,
            question="Old Question?",
            answer="Old Answer.",
        )
        response = self.admin_client.delete(f"/api/v1/admin/faqs/{faq.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"], {"deleted": True})
        self.assertFalse(TourFaq.objects.filter(id=faq.id).exists())

    def test_delete_faq_not_found(self):
        response = self.admin_client.delete("/api/v1/admin/faqs/999999")
        self.assertEqual(response.status_code, 404)

    def test_delete_faq_unauthenticated(self):
        response = self.anon_client.delete("/api/v1/admin/faqs/1")
        self.assertEqual(response.status_code, 401)

    def test_delete_faq_forbidden_customer(self):
        response = self.customer_client.delete("/api/v1/admin/faqs/1")
        self.assertEqual(response.status_code, 403)

    def test_create_guide_success(self):
        payload = {
            "full_name": "Moana Davis",
            "bio": "Experienced alpine guide.",
            "photo_url": "/media/guides/moana.jpg",
            "languages": ["English", "German"],
        }
        response = self.admin_client.post("/api/v1/admin/guides", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["full_name"], "Moana Davis")
        self.assertEqual(data["bio"], "Experienced alpine guide.")
        self.assertEqual(data["photo_url"], "/media/guides/moana.jpg")
        self.assertEqual(data["languages"], ["English", "German"])

    def test_create_guide_validation_error(self):
        response = self.admin_client.post("/api/v1/admin/guides", {}, format="json")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")
        self.assertIn("full_name", response.data["error"]["fields"])

    def test_create_guide_unauthenticated(self):
        response = self.anon_client.post("/api/v1/admin/guides", {}, format="json")
        self.assertEqual(response.status_code, 401)

    def test_create_guide_forbidden_customer(self):
        response = self.customer_client.post("/api/v1/admin/guides", {}, format="json")
        self.assertEqual(response.status_code, 403)

    def test_update_guide_success(self):
        payload = {"bio": "Local guide for 13 years."}
        response = self.admin_client.put(
            f"/api/v1/admin/guides/{self.guide.id}", payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["bio"], "Local guide for 13 years.")
        self.assertEqual(data["full_name"], "Hemi Walker")

    def test_update_guide_not_found(self):
        response = self.admin_client.put(
            "/api/v1/admin/guides/999999", {"bio": "Test"}, format="json"
        )
        self.assertEqual(response.status_code, 404)

    def test_update_guide_unauthenticated(self):
        response = self.anon_client.put(f"/api/v1/admin/guides/{self.guide.id}", {}, format="json")
        self.assertEqual(response.status_code, 401)

    def test_update_guide_forbidden_customer(self):
        response = self.customer_client.put(
            f"/api/v1/admin/guides/{self.guide.id}", {}, format="json"
        )
        self.assertEqual(response.status_code, 403)

    def test_create_category_success(self):
        response = self.admin_client.post(
            "/api/v1/admin/categories", {"name": "Food"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], "Food")
        self.assertTrue(Category.objects.filter(name="Food").exists())

    def test_create_category_duplicate(self):
        response = self.admin_client.post(
            "/api/v1/admin/categories", {"name": "water"}, format="json"
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")
        self.assertIn("name", response.data["error"]["fields"])

    def test_create_category_blank(self):
        response = self.admin_client.post(
            "/api/v1/admin/categories", {"name": "   "}, format="json"
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")
        self.assertIn("name", response.data["error"]["fields"])

    def test_create_category_unauthenticated(self):
        response = self.anon_client.post(
            "/api/v1/admin/categories", {"name": "Food"}, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_create_category_forbidden_customer(self):
        response = self.customer_client.post(
            "/api/v1/admin/categories", {"name": "Food"}, format="json"
        )
        self.assertEqual(response.status_code, 403)
