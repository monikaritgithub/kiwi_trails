"""Tests for sample booking and attendance seeding."""

from collections import Counter
from decimal import ROUND_HALF_UP, Decimal
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db.models import Sum
from django.test import TestCase

from apps.accounts.models import User
from apps.bookings.management.seed_data import SEED_BOOKING_REFERENCES
from apps.bookings.models import Attendance, Booking
from apps.coupons.models import Coupon
from apps.departures.models import Departure
from apps.reviews.models import Review


class SeedBookingsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_core", stdout=StringIO())

    def run_seed(self, **options):
        output = StringIO()
        call_command("seed_bookings", stdout=output, **options)
        return output.getvalue()

    def seed_bookings(self):
        return Booking.objects.filter(
            booking_reference__in=SEED_BOOKING_REFERENCES,
        )

    def booking(self, number):
        return Booking.objects.get(
            booking_reference=f"KT-SEED-{number:03d}",
        )

    def create_other_booking(self):
        source = self.booking(2)
        return Booking.objects.create(
            booking_reference="KT-OTHER-001",
            user=source.user,
            departure=source.departure,
            traveller_count=1,
            price_per_person=source.price_per_person,
            subtotal=source.price_per_person,
            discount_amount=Decimal("0.00"),
            total_price=source.price_per_person,
            status="pending",
        )

    def test_creates_sixteen_bookings(self):
        output = self.run_seed()

        self.assertEqual(self.seed_bookings().count(), 16)
        self.assertIn("16 bookings created", output)
        self.assertIn("3 attendance records", output)

    def test_status_distribution(self):
        self.run_seed()

        counts = Counter(
            self.seed_bookings().values_list("status", flat=True),
        )
        self.assertEqual(
            counts,
            {
                "pending": 4,
                "approved": 4,
                "rejected": 2,
                "cancelled": 2,
                "completed": 4,
            },
        )

    def test_repeat_run_does_not_duplicate_records(self):
        self.run_seed()
        booking_ids = set(
            self.seed_bookings().values_list("pk", flat=True),
        )
        attendance_ids = set(
            Attendance.objects.values_list("pk", flat=True),
        )

        output = self.run_seed()

        self.assertEqual(
            set(self.seed_bookings().values_list("pk", flat=True)),
            booking_ids,
        )
        self.assertEqual(
            set(Attendance.objects.values_list("pk", flat=True)),
            attendance_ids,
        )
        self.assertIn("0 bookings created", output)

    def test_reset_recreates_only_seed_records(self):
        self.run_seed()
        old_ids = set(
            self.seed_bookings().values_list("pk", flat=True),
        )
        other = self.create_other_booking()

        self.run_seed(reset=True)

        new_ids = set(
            self.seed_bookings().values_list("pk", flat=True),
        )
        self.assertEqual(len(new_ids), 16)
        self.assertTrue(old_ids.isdisjoint(new_ids))
        self.assertTrue(Booking.objects.filter(pk=other.pk).exists())
        self.assertEqual(
            Attendance.objects.filter(
                booking__booking_reference__in=SEED_BOOKING_REFERENCES,
            ).count(),
            3,
        )

    def test_reset_preserves_reviews_and_bookings(self):
        self.run_seed()
        booking = self.booking(13)
        review = Review.objects.create(
            booking=booking,
            user=booking.user,
            tour=booking.departure.tour,
            rating=5,
            comment="Keep this review.",
        )
        old_ids = set(
            self.seed_bookings().values_list("pk", flat=True),
        )

        with self.assertRaisesMessage(CommandError, "have reviews"):
            self.run_seed(reset=True)

        self.assertTrue(Review.objects.filter(pk=review.pk).exists())
        self.assertEqual(
            set(self.seed_bookings().values_list("pk", flat=True)),
            old_ids,
        )
        self.assertEqual(Attendance.objects.count(), 3)

    def test_missing_admin_returns_clear_error(self):
        User.objects.filter(
            email="admin@kiwitrails.test",
        ).delete()

        with self.assertRaisesMessage(
            CommandError,
            "administrator missing",
        ):
            self.run_seed()

        self.assertFalse(self.seed_bookings().exists())

    def test_missing_customer_returns_clear_error(self):
        User.objects.filter(
            email="aroha@kiwitrails.test",
        ).delete()

        with self.assertRaisesMessage(
            CommandError,
            "aroha@kiwitrails.test missing",
        ):
            self.run_seed()

        self.assertFalse(self.seed_bookings().exists())

    def test_missing_coupon_returns_clear_error(self):
        Coupon.objects.filter(code="SUMMER10").delete()

        with self.assertRaisesMessage(
            CommandError,
            "SUMMER10 missing",
        ):
            self.run_seed()

        self.assertFalse(self.seed_bookings().exists())

    def test_missing_past_departure_rolls_back_partial_creation(self):
        Departure.objects.filter(status="completed").delete()

        with self.assertRaisesMessage(
            CommandError,
            "No suitable 'past' departure",
        ):
            self.run_seed()

        self.assertFalse(self.seed_bookings().exists())
        self.assertFalse(Attendance.objects.exists())

    def test_full_departure_holds_exactly_four_seats(self):
        self.run_seed()
        pending = self.booking(1)
        approved = self.booking(5)

        self.assertEqual(pending.departure_id, approved.departure_id)
        self.assertEqual(pending.departure.capacity, 4)

        held = Booking.objects.filter(
            departure=pending.departure,
            status__in=["pending", "approved", "completed"],
        ).aggregate(total=Sum("traveller_count"))["total"]

        self.assertEqual(held, 4)

    def test_no_departure_is_overbooked(self):
        self.run_seed()

        for departure in Departure.objects.all():
            with self.subTest(departure=departure.pk):
                held = (
                    Booking.objects.filter(
                        departure=departure,
                        status__in=["pending", "approved", "completed"],
                    ).aggregate(total=Sum("traveller_count"))["total"]
                    or 0
                )

                self.assertLessEqual(held, departure.capacity)

    def test_saved_prices_and_discounts_are_correct(self):
        self.run_seed()

        for booking in self.seed_bookings().select_related(
            "departure__tour",
            "coupon",
        ):
            with self.subTest(reference=booking.booking_reference):
                expected_subtotal = (
                    booking.departure.tour.price_per_person * booking.traveller_count
                )
                discount = Decimal("0.00")
                if booking.coupon_id:
                    coupon = booking.coupon
                    if coupon.discount_type == "percent":
                        discount = expected_subtotal * coupon.discount_value / Decimal("100")
                    else:
                        discount = coupon.discount_value
                    discount = min(
                        expected_subtotal,
                        discount,
                    ).quantize(
                        Decimal("0.01"),
                        rounding=ROUND_HALF_UP,
                    )

                self.assertEqual(
                    booking.price_per_person,
                    booking.departure.tour.price_per_person,
                )
                self.assertEqual(booking.subtotal, expected_subtotal)
                self.assertEqual(booking.discount_amount, discount)
                self.assertEqual(
                    booking.total_price,
                    expected_subtotal - discount,
                )

    def test_coupon_usage_is_stable_on_repeat_and_reset(self):
        self.run_seed()

        self.assertEqual(
            self.seed_bookings().filter(coupon__isnull=False).count(),
            2,
        )
        for code in ("SUMMER10", "WELCOME20"):
            self.assertEqual(
                Coupon.objects.get(code=code).times_used,
                1,
            )

        self.run_seed()
        self.run_seed(reset=True)

        for code in ("SUMMER10", "WELCOME20"):
            self.assertEqual(
                Coupon.objects.get(code=code).times_used,
                1,
            )

    def test_rejected_and_cancelled_bookings_have_reasons(self):
        self.run_seed()

        for booking in self.seed_bookings().filter(
            status__in=["rejected", "cancelled"],
        ):
            with self.subTest(reference=booking.booking_reference):
                self.assertTrue(booking.status_reason)
                if booking.status == "cancelled":
                    self.assertIsNotNone(booking.cancelled_at)
                else:
                    self.assertIsNone(booking.cancelled_at)

    def test_attendance_distribution_and_audit_fields(self):
        self.run_seed()
        attendance = Attendance.objects.filter(
            booking__booking_reference__in=SEED_BOOKING_REFERENCES,
        ).select_related("booking", "marked_by")

        self.assertEqual(
            Counter(attendance.values_list("status", flat=True)),
            {"present": 2, "absent": 1},
        )

        for record in attendance:
            self.assertEqual(record.booking.status, "completed")
            self.assertEqual(
                record.marked_by.email,
                "admin@kiwitrails.test",
            )
            self.assertIsNotNone(record.marked_at)

        self.assertFalse(
            Attendance.objects.filter(booking=self.booking(16)).exists(),
        )

    def test_notes_and_traveller_counts(self):
        self.run_seed()

        self.assertTrue(self.booking(3).dietary_requirements)
        self.assertTrue(self.booking(6).accessibility_needs)
        self.assertEqual(
            set(
                self.seed_bookings().values_list(
                    "traveller_count",
                    flat=True,
                ),
            ),
            {1, 2, 3, 4},
        )

    def test_reference_collision_preserves_existing_customer(self):
        self.run_seed()
        booking = self.booking(1)
        other_customer = User.objects.get(
            email="tane@kiwitrails.test",
        )
        booking.user = other_customer
        booking.save(update_fields=["user"])

        with self.assertRaisesMessage(
            CommandError,
            "belongs to another customer",
        ):
            self.run_seed(reset=True)

        booking.refresh_from_db()
        self.assertEqual(booking.user_id, other_customer.pk)
        self.assertEqual(self.seed_bookings().count(), 16)

    def test_failed_reset_restores_original_records(self):
        self.run_seed()
        old_ids = set(
            self.seed_bookings().values_list("pk", flat=True),
        )
        Departure.objects.filter(
            status="scheduled",
        ).update(status="cancelled")

        with self.assertRaisesMessage(
            CommandError,
            "No suitable 'full' departure",
        ):
            self.run_seed(reset=True)

        self.assertEqual(
            set(self.seed_bookings().values_list("pk", flat=True)),
            old_ids,
        )
        self.assertEqual(Attendance.objects.count(), 3)
