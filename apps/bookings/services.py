"""Booking service helpers for reservations and attendance.
Provides departure booking completion and completed booking retrieval.
Processes status transitions for tour bookings.
"""

from decimal import ROUND_HALF_UP, Decimal

from django.utils import timezone

from apps.bookings.models import Booking, BookingStatus
from apps.catalog.models import TourStatus
from apps.core.exceptions import BookingClosed, NotFound, SeatsUnavailable
from apps.coupons.services import apply_coupon
from apps.departures.models import Departure, DepartureStatus


def complete_bookings_for_departure(departure):
    departure.bookings.filter(status=BookingStatus.APPROVED).update(status=BookingStatus.COMPLETED)


def get_completed_booking_for_user(booking_id, user):
    try:
        return Booking.objects.select_related("departure__tour").get(
            id=booking_id,
            user=user,
            status=BookingStatus.COMPLETED,
        )
    except (Booking.DoesNotExist, ValueError):
        return None


def calculate_booking_quote(departure_id, traveller_count, coupon_code=None):
    from apps.departures.services import get_seats_taken

    departure = Departure.objects.select_related("tour").filter(id=departure_id).first()

    if departure is None:
        raise NotFound("Departure not found.")

    now = timezone.now()
    if (
        departure.status != DepartureStatus.SCHEDULED
        or departure.tour.status != TourStatus.ACTIVE
        or now >= departure.booking_deadline
        or now >= departure.start_datetime
    ):
        raise BookingClosed("Bookings are closed for this departure.")

    seats_left = departure.capacity - get_seats_taken(departure)
    if traveller_count > seats_left:
        raise SeatsUnavailable(
            "There are not enough available seats.",
            {"traveller_count": f"Only {max(0, seats_left)} seats are available."},
        )

    price_per_person = departure.tour.price_per_person
    subtotal = (price_per_person * traveller_count).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    coupon = None
    discount_amount = Decimal("0.00")
    total_price = subtotal

    if coupon_code:
        coupon, discount_amount, total_price = apply_coupon(coupon_code, subtotal)

    return {
        "departure_id": departure.id,
        "traveller_count": traveller_count,
        "price_per_person": price_per_person,
        "subtotal": subtotal,
        "discount_amount": discount_amount,
        "total_price": total_price,
        "coupon_code": coupon.code if coupon else None,
        "seats_left": seats_left,
    }
