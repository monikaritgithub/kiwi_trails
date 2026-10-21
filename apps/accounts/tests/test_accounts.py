"""Automated tests for accounts authentication and profile endpoints.
Tests success and error scenarios across all five accounts calls.
Verifies response status codes and error payloads match specifications.
"""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.testing import make_client, make_customer


class AccountsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/v1/auth/register"
        self.login_url = "/api/v1/auth/login"
        self.logout_url = "/api/v1/auth/logout"
        self.me_url = "/api/v1/users/me"

    def test_register_success(self):
        payload = {
            "full_name": "Aroha Smith",
            "email": "aroha@example.com",
            "password": "Password123!",
            "phone": "021 123 4567",
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["full_name"], "Aroha Smith")
        self.assertEqual(data["email"], "aroha@example.com")
        self.assertEqual(data["phone"], "021 123 4567")
        self.assertEqual(data["role"], "customer")
        self.assertIn("id", data)
        self.assertIn("created_at", data)
        self.assertNotIn("password", data)

    def test_register_email_taken(self):
        make_customer(email="aroha@example.com", full_name="Aroha Smith")
        payload = {
            "full_name": "Aroha Smith",
            "email": "Aroha@example.com",
            "password": "Password123!",
            "phone": "021 123 4567",
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, 409)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "EMAIL_TAKEN")
        self.assertEqual(response.data["error"]["message"], "Email is already used.")
        self.assertEqual(response.data["error"]["fields"], {"email": "Email is already used."})

    def test_register_validation_error(self):
        payload = {
            "full_name": "A",
            "email": "not-an-email",
            "password": "short",
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, 422)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")
        self.assertIn("full_name", response.data["error"]["fields"])
        self.assertIn("email", response.data["error"]["fields"])
        self.assertIn("password", response.data["error"]["fields"])

    def test_login_success(self):
        make_customer(email="aroha@example.com", password="Password123!")
        payload = {
            "email": "aroha@example.com",
            "password": "Password123!",
        }
        response = self.client.post(self.login_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertIn("token", data)
        self.assertIn("expires_at", data)
        self.assertEqual(data["user"]["email"], "aroha@example.com")
        self.assertEqual(data["user"]["role"], "customer")

    def test_login_unauthenticated_wrong_password(self):
        make_customer(email="aroha@example.com", password="Password123!")
        payload = {
            "email": "aroha@example.com",
            "password": "WrongPassword123!",
        }
        response = self.client.post(self.login_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "UNAUTHENTICATED")
        self.assertEqual(response.data["error"]["message"], "Email or password is wrong.")

    def test_login_unauthenticated_wrong_email(self):
        payload = {
            "email": "nonexistent@example.com",
            "password": "Password123!",
        }
        response = self.client.post(self.login_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "UNAUTHENTICATED")
        self.assertEqual(response.data["error"]["message"], "Email or password is wrong.")

    def test_login_validation_error(self):
        payload = {
            "email": "invalid-email",
            "password": "",
        }
        response = self.client.post(self.login_url, payload, format="json")
        self.assertEqual(response.status_code, 422)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")

    def test_logout_success(self):
        user = make_customer(email="aroha@example.com")
        auth_client = make_client(user)
        response = auth_client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["message"], "Logged out")

        me_response = auth_client.get(self.me_url)
        self.assertEqual(me_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_unauthenticated(self):
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "UNAUTHENTICATED")

    def test_get_me_success(self):
        user = make_customer(email="aroha@example.com", full_name="Aroha Smith")
        auth_client = make_client(user)
        response = auth_client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["email"], "aroha@example.com")
        self.assertEqual(data["full_name"], "Aroha Smith")
        self.assertEqual(data["role"], "customer")

    def test_get_me_unauthenticated(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "UNAUTHENTICATED")

    def test_put_me_update_name_and_phone(self):
        user = make_customer(email="aroha@example.com", full_name="Aroha Smith")
        auth_client = make_client(user)
        payload = {
            "full_name": "Aroha Smith-Wiremu",
            "phone": None,
        }
        response = auth_client.put(self.me_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        data = response.data["data"]
        self.assertEqual(data["full_name"], "Aroha Smith-Wiremu")
        self.assertIsNone(data["phone"])

        user.refresh_from_db()
        self.assertEqual(user.full_name, "Aroha Smith-Wiremu")
        self.assertIsNone(user.phone)

    def test_put_me_update_password_success(self):
        user = make_customer(email="aroha@example.com", password="Password123!")
        auth_client = make_client(user)
        payload = {
            "current_password": "Password123!",
            "new_password": "NewPassword456!",
        }
        response = auth_client.put(self.me_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        user.refresh_from_db()
        self.assertTrue(user.check_password("NewPassword456!"))

    def test_put_me_wrong_current_password(self):
        user = make_customer(email="aroha@example.com", password="Password123!")
        auth_client = make_client(user)
        payload = {
            "current_password": "WrongPassword123!",
            "new_password": "NewPassword456!",
        }
        response = auth_client.put(self.me_url, payload, format="json")
        self.assertEqual(response.status_code, 422)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")
        self.assertEqual(response.data["error"]["message"], "Current password is wrong.")
        self.assertEqual(
            response.data["error"]["fields"],
            {"current_password": "Current password is wrong."},
        )

    def test_put_me_missing_one_password(self):
        user = make_customer(email="aroha@example.com", password="Password123!")
        auth_client = make_client(user)
        payload = {
            "new_password": "NewPassword456!",
        }
        response = auth_client.put(self.me_url, payload, format="json")
        self.assertEqual(response.status_code, 422)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")

    def test_put_me_unauthenticated(self):
        payload = {"full_name": "New Name"}
        response = self.client.put(self.me_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"]["code"], "UNAUTHENTICATED")
