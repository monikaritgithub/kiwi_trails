"""Booking service helpers for reservations and attendance.
Provides departure booking completion and completed booking retrieval.
Processes status transitions for tour bookings.
"""

from apps.bookings.models import Booking, BookingStatus


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
