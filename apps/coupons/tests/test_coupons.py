"""Automated tests for customer and admin coupon endpoints.
Tests coupon validation calculations limits and administrative updates.
Verifies percentage rounding fixed ceilings and invalid code errors.
"""

from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.testing import make_admin, make_client, make_customer
from apps.coupons.models import Coupon, CouponDiscountType
from apps.coupons.services import mark_coupon_used


class CouponsTests(TestCase):
    def setUp(self):
        self.anon_client = APIClient()
        self.admin = make_admin(email="admin@kiwitrails.test")
        self.admin_client = make_client(self.admin)
        self.customer = make_customer(email="customer@kiwitrails.test")
        self.customer_client = make_client(self.customer)

        now = timezone.now()
        self.percent_coupon = Coupon.objects.create(
            code="SUMMER10",
            discount_type=CouponDiscountType.PERCENT,
            discount_value=Decimal("10.00"),
            expires_at=now + timedelta(days=30),
            max_uses=100,
            times_used=0,
            is_active=True,
        )
        self.fixed_coupon = Coupon.objects.create(
            code="WELCOME20",
            discount_type=CouponDiscountType.FIXED,
            discount_value=Decimal("20.00"),
            expires_at=now + timedelta(days=30),
            max_uses=50,
            times_used=0,
            is_active=True,
        )
        self.expired_coupon = Coupon.objects.create(
            code="EXPIRED5",
            discount_type=CouponDiscountType.PERCENT,
            discount_value=Decimal("5.00"),
            expires_at=now - timedelta(days=1),
            max_uses=10,
            times_used=0,
            is_active=True,
        )
        self.inactive_coupon = Coupon.objects.create(
            code="SWITCHEDOFF",
            discount_type=CouponDiscountType.PERCENT,
            discount_value=Decimal("15.00"),
            expires_at=now + timedelta(days=30),
            max_uses=10,
            times_used=0,
            is_active=False,
        )
        self.exhausted_coupon = Coupon.objects.create(
            code="ONEUSE",
            discount_type=CouponDiscountType.FIXED,
            discount_value=Decimal("10.00"),
            expires_at=now + timedelta(days=30),
            max_uses=1,
            times_used=1,
            is_active=True,
        )

    def test_validate_percent_coupon_success(self):
        payload = {"code": "summer10", "subtotal": 498.00}
        response = self.customer_client.post("/api/v1/coupons/validate", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["code"], "SUMMER10")
        self.assertEqual(data["discount_type"], "percent")
        self.assertEqual(data["discount_value"], 10.00)
        self.assertEqual(data["discount_amount"], 49.80)
        self.assertEqual(data["new_total"], 448.20)

    def test_validate_percent_rounding_half_up(self):
        Coupon.objects.create(
            code="ROUND15",
            discount_type=CouponDiscountType.PERCENT,
            discount_value=Decimal("15.00"),
            expires_at=timezone.now() + timedelta(days=10),
            is_active=True,
        )
        payload = {"code": "ROUND15", "subtotal": 99.95}
        response = self.customer_client.post("/api/v1/coupons/validate", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["discount_amount"], 14.99)
        self.assertEqual(response.data["data"]["new_total"], 84.96)

    def test_validate_fixed_coupon_success(self):
        payload = {"code": "WELCOME20", "subtotal": 100.00}
        response = self.customer_client.post("/api/v1/coupons/validate", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data["data"]
        self.assertEqual(data["discount_amount"], 20.00)
        self.assertEqual(data["new_total"], 80.00)

    def test_validate_fixed_coupon_floor_zero(self):
        payload = {"code": "WELCOME20", "subtotal": 15.00}
        response = self.customer_client.post("/api/v1/coupons/validate", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data["data"]
        self.assertEqual(data["discount_amount"], 15.00)
        self.assertEqual(data["new_total"], 0.00)

    def test_validate_coupon_unauthenticated(self):
        response = self.anon_client.post(
            "/api/v1/coupons/validate", {"code": "SUMMER10", "subtotal": 100.00}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error"]["code"], "UNAUTHENTICATED")

    def test_validate_coupon_invalid_subtotal(self):
        response = self.customer_client.post(
            "/api/v1/coupons/validate", {"code": "SUMMER10", "subtotal": 0}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")
        self.assertIn("subtotal", response.data["error"]["fields"])

    def test_validate_coupon_unknown_code(self):
        response = self.customer_client.post(
            "/api/v1/coupons/validate", {"code": "UNKNOWN99", "subtotal": 100.00}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data["error"]["code"], "COUPON_INVALID")
        self.assertIn("code", response.data["error"]["fields"])

    def test_validate_coupon_inactive(self):
        response = self.customer_client.post(
            "/api/v1/coupons/validate", {"code": "SWITCHEDOFF", "subtotal": 100.00}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data["error"]["code"], "COUPON_INVALID")

    def test_validate_coupon_expired(self):
        response = self.customer_client.post(
            "/api/v1/coupons/validate", {"code": "EXPIRED5", "subtotal": 100.00}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data["error"]["code"], "COUPON_INVALID")

    def test_validate_coupon_exhausted(self):
        response = self.customer_client.post(
            "/api/v1/coupons/validate", {"code": "ONEUSE", "subtotal": 100.00}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data["error"]["code"], "COUPON_INVALID")

    def test_list_admin_coupons_success(self):
        response = self.admin_client.get("/api/v1/admin/coupons")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertGreaterEqual(data["total"], 5)
        codes = [item["code"] for item in data["items"]]
        self.assertIn("SUMMER10", codes)
        self.assertIn("WELCOME20", codes)

    def test_list_admin_coupons_unauthenticated(self):
        response = self.anon_client.get("/api/v1/admin/coupons")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_admin_coupons_forbidden_customer(self):
        response = self.customer_client.get("/api/v1/admin/coupons")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_coupon_success(self):
        payload = {
            "code": "autumn25",
            "discount_type": "percent",
            "discount_value": 25.00,
            "expires_at": (timezone.now() + timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "max_uses": 200,
        }
        response = self.admin_client.post("/api/v1/admin/coupons", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["code"], "AUTUMN25")
        self.assertEqual(data["discount_type"], "percent")
        self.assertEqual(data["discount_value"], 25.00)
        self.assertEqual(data["max_uses"], 200)
        self.assertEqual(data["times_used"], 0)
        self.assertTrue(data["is_active"])

    def test_create_coupon_validation_errors(self):
        payload = {
            "code": "SUMMER10",
            "discount_type": "percent",
            "discount_value": 150.00,
            "expires_at": (timezone.now() - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "max_uses": 0,
        }
        response = self.admin_client.post("/api/v1/admin/coupons", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")
        fields = response.data["error"]["fields"]
        self.assertIn("code", fields)
        self.assertIn("discount_value", fields)
        self.assertIn("expires_at", fields)
        self.assertIn("max_uses", fields)

    def test_create_coupon_unauthenticated(self):
        response = self.anon_client.post("/api/v1/admin/coupons", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_coupon_forbidden_customer(self):
        response = self.customer_client.post("/api/v1/admin/coupons", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_coupon_success(self):
        payload = {"is_active": False, "max_uses": 75}
        response = self.admin_client.put(
            f"/api/v1/admin/coupons/{self.fixed_coupon.id}",
            payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertFalse(data["is_active"])
        self.assertEqual(data["max_uses"], 75)
        self.assertEqual(data["code"], "WELCOME20")

    def test_update_coupon_not_found(self):
        response = self.admin_client.put(
            "/api/v1/admin/coupons/999999",
            {"is_active": False},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_coupon_unauthenticated(self):
        response = self.anon_client.put(
            f"/api/v1/admin/coupons/{self.fixed_coupon.id}",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_coupon_forbidden_customer(self):
        response = self.customer_client.put(
            f"/api/v1/admin/coupons/{self.fixed_coupon.id}",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mark_coupon_used_helper(self):
        self.assertEqual(self.percent_coupon.times_used, 0)
        mark_coupon_used(self.percent_coupon)
        self.assertEqual(self.percent_coupon.times_used, 1)
