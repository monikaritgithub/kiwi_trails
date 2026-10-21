"""
Tests for core response formatting and exception handling.
Verifies success and error payloads match Kiwi Trails specifications.
"""

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from apps.core.exceptions import ValidationFailed
from apps.core.renderers import ApiRenderer


class DummySuccessView(APIView):
    renderer_classes = [ApiRenderer]

    def get(self, request):
        return Response({"id": 1, "name": "Milford Sound"})


class DummyErrorView(APIView):
    renderer_classes = [ApiRenderer]

    def get(self, request):
        raise ValidationFailed("Invalid input.", {"code": "Required field."})


class ResponseFormatTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_success_response_shape(self):
        request = self.factory.get("/")
        view = DummySuccessView.as_view()
        response = view(request)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"], {"id": 1, "name": "Milford Sound"})

    def test_error_response_shape(self):
        request = self.factory.get("/")
        view = DummyErrorView.as_view()
        response = view(request)
        response.render()

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertFalse(response.data["success"])
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")
        self.assertEqual(response.data["error"]["message"], "Invalid input.")
        self.assertEqual(response.data["error"]["fields"], {"code": "Required field."})
