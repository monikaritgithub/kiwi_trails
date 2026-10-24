"""Tests for booking invoice downloads.
Checks access, permitted statuses, PDF responses, and unchanged booking data.
"""

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.bookings.models import Booking, BookingStatus
from apps.catalog.models import Category, Tour
from apps.core.testing import make_admin, make_client, make_customer
from apps.departures.models import Departure


class BookingInvoiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = make_customer(
            email="invoice@kiwitrails.test",
            full_name="Māia Rōpata",
        )
        cls.other_customer = make_customer(email="other-invoice@kiwitrails.test")
        cls.admin = make_admin(email="invoice-admin@kiwitrails.test")

        category = Category.objects.create(name="Invoice Tours")
        cls.tour = Tour.objects.create(
            title="Taupō Lake Cruise",
            description="A guided lake cruise.",
            location="Taupō",
            category=category,
            price_per_person=Decimal("150.00"),
            duration_days=1,
            itinerary="Meet at the lake.",
        )

        now = timezone.now()
        cls.departure = Departure.objects.create(
            tour=cls.tour,
            start_datetime=now + timedelta(days=30),
            booking_deadline=now + timedelta(days=25),
            capacity=10,
        )

        cls.booking = Booking.objects.create(
            booking_reference="KT-INVOICE1",
            user=cls.customer,
            departure=cls.departure,
            traveller_count=2,
            price_per_person=Decimal("150.00"),
            subtotal=Decimal("300.00"),
            discount_amount=Decimal("30.00"),
            total_price=Decimal("270.00"),
            status=BookingStatus.APPROVED,
        )

    def setUp(self):
        self.client = make_client(self.customer)
        self.url = f"/api/v1/bookings/{self.booking.id}/invoice"

    def assert_pdf_response(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF-"))
        self.assertTrue(response.content.rstrip().endswith(b"%%EOF"))
        self.assertGreater(len(response.content), 1000)

    def assert_error(self, response, status_code, code):
        self.assertEqual(response.status_code, status_code)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], code)

    def test_owner_can_download_approved_booking_invoice(self):
        response = self.client.get(self.url)

        self.assert_pdf_response(response)

    def test_owner_can_download_completed_booking_invoice(self):
        Booking.objects.filter(pk=self.booking.pk).update(status=BookingStatus.COMPLETED)

        response = self.client.get(self.url)

        self.assert_pdf_response(response)

    def test_admin_can_download_customer_invoice(self):
        response = make_client(self.admin).get(self.url)

        self.assert_pdf_response(response)

    def test_other_customer_cannot_download_invoice(self):
        with patch("apps.bookings.views.build_booking_invoice") as generator:
            response = make_client(self.other_customer).get(self.url)

        self.assert_error(response, 403, "FORBIDDEN")
        generator.assert_not_called()

    def test_anonymous_user_cannot_download_invoice(self):
        with patch("apps.bookings.views.build_booking_invoice") as generator:
            response = APIClient().get(self.url)

        self.assert_error(response, 401, "UNAUTHENTICATED")
        generator.assert_not_called()

    def test_missing_booking_returns_not_found(self):
        missing_id = self.booking.id + 1000

        response = self.client.get(f"/api/v1/bookings/{missing_id}/invoice")

        self.assert_error(response, 404, "NOT_FOUND")

    def test_disallowed_statuses_do_not_generate_invoice(self):
        for booking_status in [
            BookingStatus.PENDING,
            BookingStatus.REJECTED,
            BookingStatus.CANCELLED,
        ]:
            with self.subTest(status=booking_status):
                Booking.objects.filter(pk=self.booking.pk).update(status=booking_status)

                with patch("apps.bookings.views.build_booking_invoice") as generator:
                    response = self.client.get(self.url)

                self.assert_error(response, 403, "FORBIDDEN")
                generator.assert_not_called()

    def test_admin_cannot_bypass_invoice_status_rule(self):
        Booking.objects.filter(pk=self.booking.pk).update(status=BookingStatus.PENDING)

        response = make_client(self.admin).get(self.url)

        self.assert_error(response, 403, "FORBIDDEN")

    def test_download_filename_and_cache_headers(self):
        response = self.client.get(self.url)

        self.assert_pdf_response(response)
        self.assertEqual(
            response["Content-Disposition"],
            'attachment; filename="invoice-KT-INVOICE1.pdf"',
        )
        self.assertEqual(response["Cache-Control"], "private, no-store")

    def test_download_does_not_modify_booking_or_capacity(self):
        before = Booking.objects.values().get(pk=self.booking.pk)
        booking_count = Booking.objects.count()

        response = self.client.get(self.url)

        self.assert_pdf_response(response)
        self.assertEqual(
            Booking.objects.values().get(pk=self.booking.pk),
            before,
        )
        self.assertEqual(Booking.objects.count(), booking_count)
        self.departure.refresh_from_db()
        self.assertEqual(self.departure.capacity, 10)

    def test_generator_receives_saved_booking_prices(self):
        Tour.objects.filter(pk=self.tour.pk).update(price_per_person=Decimal("250.00"))

        with patch(
            "apps.bookings.views.build_booking_invoice",
            return_value=b"%PDF-1.4\n%%EOF",
        ) as generator:
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        generator.assert_called_once()
        booking = generator.call_args.args[0]
        self.assertEqual(booking.price_per_person, Decimal("150.00"))
        self.assertEqual(booking.subtotal, Decimal("300.00"))
        self.assertEqual(booking.discount_amount, Decimal("30.00"))
        self.assertEqual(booking.total_price, Decimal("270.00"))

    def test_special_characters_and_long_names_generate_pdf(self):
        Tour.objects.filter(pk=self.tour.pk).update(
            title="Taupō & Rotorua <Explorer> " + "Scenic " * 15
        )
        type(self.customer).objects.filter(pk=self.customer.pk).update(
            full_name="Māia & Hēmi <Rōpata>"
        )

        response = self.client.get(self.url)

        self.assert_pdf_response(response)
