"""Booking service helpers for reservations and attendance.
Calculates price previews and creates customer bookings.
Provides booking completion, retrieval, and SQLite lock retries.
"""

import secrets
import sqlite3
import string
from datetime import timedelta
from datetime import timezone as datetime_timezone
from decimal import ROUND_HALF_UP, Decimal
from time import sleep

from django.db import OperationalError, connection, transaction
from django.db.models import F, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.bookings.models import Booking, BookingStatus
from apps.catalog.models import TourStatus
from apps.core.exceptions import (
    ApiError,
    BookingClosed,
    CancellationNotAllowed,
    Forbidden,
    InvalidStatusChange,
    NotFound,
    SeatsUnavailable,
    ValidationFailed,
)
from apps.coupons.models import Coupon
from apps.coupons.services import apply_coupon, mark_coupon_used
from apps.departures.models import Departure, DepartureStatus


class BookingBusy(ApiError):
    code = "BOOKING_BUSY"
    status_code = 503


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


def generate_booking_reference():
    characters = string.ascii_uppercase + string.digits

    while True:
        suffix = "".join(secrets.choice(characters) for _ in range(6))
        reference = f"KT-{suffix}"
        if not Booking.objects.filter(booking_reference=reference).exists():
            return reference


def _create_booking_once(user, departure_id, traveller_count, coupon_code=None, **preferences):
    with transaction.atomic():
        matched = Departure.objects.filter(id=departure_id).update(capacity=F("capacity"))
        if not matched:
            raise NotFound("Departure not found.")

        quote = calculate_booking_quote(
            departure_id=departure_id,
            traveller_count=traveller_count,
            coupon_code=coupon_code,
        )

        coupon = None
        if quote["coupon_code"]:
            coupon = Coupon.objects.get(code=quote["coupon_code"])

        booking = Booking.objects.create(
            booking_reference=generate_booking_reference(),
            user=user,
            departure_id=departure_id,
            traveller_count=traveller_count,
            price_per_person=quote["price_per_person"],
            subtotal=quote["subtotal"],
            discount_amount=quote["discount_amount"],
            total_price=quote["total_price"],
            coupon=coupon,
            status=BookingStatus.PENDING,
            pickup_preference=preferences.get("pickup_preference") or "",
            dietary_requirements=preferences.get("dietary_requirements") or "",
            accessibility_needs=preferences.get("accessibility_needs") or "",
        )

        if coupon is not None:
            mark_coupon_used(coupon)

        return booking


def create_booking(user, departure_id, traveller_count, coupon_code=None, **preferences):
    for attempt in range(6):
        try:
            return _create_booking_once(
                user=user,
                departure_id=departure_id,
                traveller_count=traveller_count,
                coupon_code=coupon_code,
                **preferences,
            )
        except OperationalError as exc:
            error_code = getattr(exc.__cause__, "sqlite_errorcode", None)
            is_lock_error = (
                connection.vendor == "sqlite"
                and error_code is not None
                and (error_code & 255) in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED)
            )

            if not is_lock_error or connection.in_atomic_block:
                raise

            if attempt == 5:
                raise BookingBusy("Bookings are busy. Please try again shortly.") from exc

            sleep(0.05 * (2**attempt))


def list_customer_bookings(user, status=None):
    bookings = (
        Booking.objects.filter(user=user)
        .select_related("departure__tour", "coupon")
        .order_by("-created_at", "-id")
    )

    if status is not None:
        if status not in BookingStatus.values:
            raise ValidationFailed(
                "Invalid booking status.",
                {"status": "Use pending, approved, rejected, cancelled, or completed."},
            )
        bookings = bookings.filter(status=status)

    return bookings


def get_booking_by_id(booking_id):
    booking = (
        Booking.objects.select_related("user", "departure__tour", "coupon")
        .filter(id=booking_id)
        .first()
    )

    if booking is None:
        raise NotFound("Booking not found.")

    return booking


def _cancel_booking_once(user, booking_id, reason=None):
    with transaction.atomic():
        matched = Booking.objects.filter(id=booking_id).update(status=F("status"))
        if not matched:
            raise NotFound("Booking not found.")

        booking = get_booking_by_id(booking_id)

        if booking.user_id != user.pk:
            raise Forbidden("You can only cancel your own bookings.")

        if booking.status not in [
            BookingStatus.PENDING,
            BookingStatus.APPROVED,
        ]:
            raise InvalidStatusChange("Only pending or approved bookings can be cancelled.")

        now = timezone.now()
        cancel_deadline = booking.departure.start_datetime - timedelta(
            days=booking.departure.tour.cancellation_days
        )

        if now >= cancel_deadline:
            raise CancellationNotAllowed("This booking can no longer be cancelled online.")

        booking.status = BookingStatus.CANCELLED
        booking.status_reason = reason or ""
        booking.cancelled_at = now
        booking.save(
            update_fields=[
                "status",
                "status_reason",
                "cancelled_at",
                "updated_at",
            ]
        )

        return booking


def cancel_booking(user, booking_id, reason=None):
    for attempt in range(6):
        try:
            return _cancel_booking_once(
                user=user,
                booking_id=booking_id,
                reason=reason,
            )
        except OperationalError as exc:
            error_code = getattr(exc.__cause__, "sqlite_errorcode", None)
            is_lock_error = (
                connection.vendor == "sqlite"
                and error_code is not None
                and (error_code & 255) in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED)
            )

            if not is_lock_error or connection.in_atomic_block:
                raise

            if attempt == 5:
                raise BookingBusy("Bookings are busy. Please try again shortly.") from exc

            sleep(0.05 * (2**attempt))


def list_admin_bookings(
    *,
    status=None,
    tour_id=None,
    departure_id=None,
    date_from=None,
    date_to=None,
    search=None,
):
    bookings = Booking.objects.select_related(
        "user",
        "departure__tour",
        "coupon",
        "attendance",
    ).order_by("-created_at", "-id")

    if status is not None:
        bookings = bookings.filter(status=status)

    if tour_id is not None:
        bookings = bookings.filter(departure__tour_id=tour_id)

    if departure_id is not None:
        bookings = bookings.filter(departure_id=departure_id)

    if date_from is not None or date_to is not None:
        bookings = bookings.annotate(
            departure_date=TruncDate(
                "departure__start_datetime",
                tzinfo=datetime_timezone.utc,
            )
        )

        if date_from is not None:
            bookings = bookings.filter(departure_date__gte=date_from)

        if date_to is not None:
            bookings = bookings.filter(departure_date__lte=date_to)

    if search:
        bookings = bookings.filter(
            Q(booking_reference__icontains=search) | Q(user__full_name__icontains=search)
        )

    return bookings


def _update_booking_status_once(user, booking_id, status, reason=None):
    if not user.is_authenticated or getattr(user, "role", None) != "admin":
        raise Forbidden("Only administrators can change booking status.")

    allowed_targets = {
        BookingStatus.APPROVED,
        BookingStatus.REJECTED,
        BookingStatus.CANCELLED,
        BookingStatus.COMPLETED,
    }
    if status not in allowed_targets:
        raise ValidationFailed(
            "Invalid booking status.",
            {"status": "Use approved, rejected, cancelled, or completed."},
        )

    allowed_changes = {
        BookingStatus.PENDING: {
            BookingStatus.APPROVED,
            BookingStatus.REJECTED,
            BookingStatus.CANCELLED,
        },
        BookingStatus.APPROVED: {
            BookingStatus.CANCELLED,
            BookingStatus.COMPLETED,
        },
    }

    with transaction.atomic():
        matched = Booking.objects.filter(id=booking_id).update(status=F("status"))
        if not matched:
            raise NotFound("Booking not found.")

        booking = get_booking_by_id(booking_id)

        if status not in allowed_changes.get(booking.status, set()):
            raise InvalidStatusChange(
                f"Cannot change booking status from {booking.status} to {status}."
            )

        booking.status = status
        booking.status_reason = reason or ""

        update_fields = ["status", "status_reason", "updated_at"]

        if status == BookingStatus.CANCELLED:
            booking.cancelled_at = timezone.now()
            update_fields.append("cancelled_at")

        booking.save(update_fields=update_fields)

        return booking


def update_booking_status(user, booking_id, status, reason=None):
    for attempt in range(6):
        try:
            return _update_booking_status_once(
                user=user,
                booking_id=booking_id,
                status=status,
                reason=reason,
            )
        except OperationalError as exc:
            error_code = getattr(exc.__cause__, "sqlite_errorcode", None)
            is_lock_error = (
                connection.vendor == "sqlite"
                and error_code is not None
                and (error_code & 255) in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED)
            )

            if not is_lock_error or connection.in_atomic_block:
                raise

            if attempt == 5:
                raise BookingBusy("Bookings are busy. Please try again shortly.") from exc

            sleep(0.05 * (2**attempt))
