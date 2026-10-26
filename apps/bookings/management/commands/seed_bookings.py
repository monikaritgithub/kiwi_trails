"""Create repeatable sample bookings and attendance records."""

from decimal import ROUND_HALF_UP, Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.accounts.models import User
from apps.bookings.management.seed_data import (
    SEED_BOOKING_REFERENCES,
    SEED_BOOKINGS,
)
from apps.bookings.models import Attendance, Booking, BookingStatus
from apps.catalog.models import TourStatus
from apps.coupons.models import Coupon
from apps.departures.models import Departure, DepartureStatus
from apps.reviews.models import Review

MONEY_STEP = Decimal("0.01")
HOLDING_STATUSES = [
    BookingStatus.PENDING,
    BookingStatus.APPROVED,
    BookingStatus.COMPLETED,
]


class Command(BaseCommand):
    help = "Seed 16 sample bookings and three attendance records."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Recreate this command's bookings unless they have reviews.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        now = timezone.now()

        admin = User.objects.filter(
            email="admin@kiwitrails.test",
            role="admin",
            is_active=True,
        ).first()

        if admin is None:
            raise CommandError("Seed administrator missing. Run seed_core first.")

        customers = {}
        for short_name in ("aroha", "tane", "mei", "liam", "sione"):
            email = f"{short_name}@kiwitrails.test"
            customer = User.objects.filter(
                email=email,
                role="customer",
                is_active=True,
            ).first()

            if customer is None:
                raise CommandError(f"Seed customer {email} missing. Run seed_core first.")

            customers[short_name] = customer

        coupons = {}
        for code in ("SUMMER10", "WELCOME20"):
            coupon = Coupon.objects.filter(code=code).first()

            if coupon is None:
                raise CommandError(f"Seed coupon {code} missing. Run seed_core first.")

            coupons[code] = coupon

        own_bookings = Booking.objects.filter(
            booking_reference__in=SEED_BOOKING_REFERENCES,
        )

        # Refuse to reuse a reference belonging to another customer.
        for row in SEED_BOOKINGS:
            reference, short_name = row[:2]
            existing = own_bookings.filter(
                booking_reference=reference,
            ).first()

            if existing and existing.user_id != customers[short_name].pk:
                raise CommandError(f"{reference} belongs to another customer; no changes saved.")

        if options["reset"]:
            if Review.objects.filter(booking__in=own_bookings).exists():
                raise CommandError("Seed bookings have reviews. Reset stopped to preserve them.")

            # Attendance is deleted through the booking's CASCADE relation.
            own_bookings.delete()

        created_count = 0

        for row in SEED_BOOKINGS:
            (
                reference,
                short_name,
                booking_status,
                travellers,
                departure_kind,
                coupon_code,
                attendance_status,
            ) = row

            if Booking.objects.filter(
                booking_reference=reference,
            ).exists():
                continue

            holds_seats = booking_status in HOLDING_STATUSES
            departure = self.choose_departure(
                kind=departure_kind,
                travellers=travellers,
                holds_seats=holds_seats,
                now=now,
            )

            price = departure.tour.price_per_person
            subtotal = (price * travellers).quantize(MONEY_STEP)
            coupon = coupons.get(coupon_code)
            discount = self.calculate_discount(subtotal, coupon)

            reason = ""
            cancelled_at = None

            if booking_status == BookingStatus.REJECTED:
                reason = "Sample booking rejected by an administrator."
            elif booking_status == BookingStatus.CANCELLED:
                reason = "Sample customer changed their travel plans."
                cancelled_at = now

            booking = Booking.objects.create(
                booking_reference=reference,
                user=customers[short_name],
                departure=departure,
                traveller_count=travellers,
                price_per_person=price,
                subtotal=subtotal,
                discount_amount=discount,
                total_price=subtotal - discount,
                coupon=coupon,
                status=booking_status,
                pickup_preference="Meet at the tour meeting point",
                dietary_requirements=("Vegetarian" if reference == "KT-SEED-003" else ""),
                accessibility_needs=(
                    "Step-free access requested" if reference == "KT-SEED-006" else ""
                ),
                status_reason=reason,
                cancelled_at=cancelled_at,
            )

            if attendance_status is not None:
                Attendance.objects.create(
                    booking=booking,
                    status=attendance_status,
                    marked_by=admin,
                )

            created_count += 1

        # Preserve prior usage and avoid adding usage on repeated runs.
        for coupon in coupons.values():
            linked_bookings = Booking.objects.filter(coupon=coupon).count()

            if coupon.times_used < linked_bookings:
                coupon.times_used = linked_bookings
                coupon.save(update_fields=["times_used"])

        booking_count = Booking.objects.filter(
            booking_reference__in=SEED_BOOKING_REFERENCES,
        ).count()

        attendance_count = Attendance.objects.filter(
            booking__booking_reference__in=SEED_BOOKING_REFERENCES,
        ).count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded bookings and attendance records. "
                f"{created_count} bookings created; "
                f"{booking_count} seed bookings and "
                f"{attendance_count} attendance records available."
            )
        )
        self.stdout.write("Seed customers: Aroha, Tane, Mei, Liam and Sione.")

    def choose_departure(self, *, kind, travellers, holds_seats, now):
        departures = Departure.objects.select_related("tour").filter(
            tour__status=TourStatus.ACTIVE,
        )

        if kind == "past":
            departures = departures.filter(
                status=DepartureStatus.COMPLETED,
                start_datetime__lt=now,
            )
        else:
            departures = departures.filter(
                status=DepartureStatus.SCHEDULED,
                start_datetime__gt=now,
                booking_deadline__gt=now,
            )

            if kind == "full":
                departures = departures.filter(
                    tour__title="Tongariro Alpine Crossing",
                    capacity=4,
                )
            else:
                departures = departures.exclude(
                    tour__title="Tongariro Alpine Crossing",
                    capacity=4,
                )

        for departure in departures.order_by("start_datetime", "pk"):
            occupied = (
                Booking.objects.filter(
                    departure=departure,
                    status__in=HOLDING_STATUSES,
                ).aggregate(total=Sum("traveller_count"))["total"]
                or 0
            )

            required = travellers if holds_seats else 0

            if occupied + required <= departure.capacity:
                return departure

        raise CommandError(
            f"No suitable '{kind}' departure with enough seats. "
            "Check the seed_core departures and their dates. "
            "No changes from this command were saved."
        )

    def calculate_discount(self, subtotal, coupon):
        if coupon is None:
            return Decimal("0.00")

        if coupon.discount_type == "percent":
            discount = subtotal * coupon.discount_value / Decimal("100")
        elif coupon.discount_type == "fixed":
            discount = coupon.discount_value
        else:
            raise CommandError(f"Unsupported discount type for coupon {coupon.code}.")

        return min(
            subtotal,
            max(Decimal("0.00"), discount),
        ).quantize(
            MONEY_STEP,
            rounding=ROUND_HALF_UP,
        )
