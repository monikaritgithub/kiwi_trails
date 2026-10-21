"""Departure service helpers and domain operations for booking availability.
Calculates seats taken and checks whether bookings remain open.
Provides schedule queries calendar generation and capacity updates.
"""

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.bookings.models import BookingStatus
from apps.bookings.services import complete_bookings_for_departure
from apps.catalog.models import Tour, TourStatus
from apps.core.exceptions import CapacityConflict, NotFound, ValidationFailed
from apps.departures.models import Departure, DepartureStatus


def get_seats_taken(departure):
    res = departure.bookings.filter(
        status__in=[
            BookingStatus.PENDING,
            BookingStatus.APPROVED,
            BookingStatus.COMPLETED,
        ]
    ).aggregate(total=Sum("traveller_count"))["total"]
    return res or 0


def is_booking_open(departure):
    if departure.status != DepartureStatus.SCHEDULED:
        return False
    if getattr(departure.tour, "status", None) == TourStatus.ARCHIVED:
        return False
    now = timezone.now()
    if departure.booking_deadline < now or departure.start_datetime < now:
        return False
    taken = get_seats_taken(departure)
    return departure.capacity - taken > 0


def list_tour_departures(tour_id, user=None):
    tour = Tour.objects.filter(id=tour_id).first()
    if not tour:
        raise NotFound(f"Tour {tour_id} not found.")

    is_admin = False
    if user and getattr(user, "is_authenticated", False):
        if getattr(user, "role", "") == "admin":
            is_admin = True

    if tour.status == TourStatus.ARCHIVED and not is_admin:
        raise NotFound(f"Tour {tour_id} not found.")

    now = timezone.now()
    return (
        tour.departures.filter(
            status=DepartureStatus.SCHEDULED,
            start_datetime__gte=now,
        )
        .select_related("tour")
        .order_by("start_datetime")
    )


def get_departure_calendar(month_str):
    if not month_str or not isinstance(month_str, str):
        raise ValidationFailed(
            "Month parameter is required.",
            {"month": "Month parameter is required in YYYY-MM format."},
        )
    parts = month_str.strip().split("-")
    if len(parts) != 2 or len(parts[0]) != 4 or len(parts[1]) != 2:
        raise ValidationFailed(
            "Invalid month format.",
            {"month": "Month must be in YYYY-MM format."},
        )
    try:
        year = int(parts[0])
        month = int(parts[1])
        if year < 2000 or year > 2100 or month < 1 or month > 12:
            raise ValueError()
    except (ValueError, TypeError):
        raise ValidationFailed(
            "Invalid month format.",
            {"month": "Month must be in YYYY-MM format with a valid month."},
        )

    return (
        Departure.objects.filter(
            start_datetime__year=year,
            start_datetime__month=month,
        )
        .exclude(status=DepartureStatus.CANCELLED)
        .select_related("tour")
        .order_by("start_datetime")
    )


def create_departure(tour_id, data):
    tour = Tour.objects.filter(id=tour_id).first()
    if not tour:
        raise NotFound(f"Tour {tour_id} not found.")

    return Departure.objects.create(
        tour=tour,
        start_datetime=data["start_datetime"],
        capacity=data["capacity"],
        booking_deadline=data["booking_deadline"],
        status=DepartureStatus.SCHEDULED,
    )


def update_departure(departure_id, data):
    departure = Departure.objects.select_related("tour").filter(id=departure_id).first()
    if not departure:
        raise NotFound(f"Departure {departure_id} not found.")

    new_start = data.get("start_datetime", departure.start_datetime)
    new_deadline = data.get("booking_deadline", departure.booking_deadline)

    if "booking_deadline" in data or "start_datetime" in data:
        if new_deadline >= new_start:
            raise ValidationFailed(
                "Booking deadline must be before start datetime.",
                {"booking_deadline": "Booking deadline must be before start datetime."},
            )

    if "capacity" in data:
        new_capacity = data["capacity"]
        seats_taken = get_seats_taken(departure)
        if new_capacity < seats_taken:
            raise CapacityConflict(
                f"Capacity cannot be lower than the {seats_taken} seats already taken.",
                {"capacity": f"Must be at least {seats_taken}."},
            )
        departure.capacity = new_capacity

    if "start_datetime" in data:
        departure.start_datetime = data["start_datetime"]
    if "booking_deadline" in data:
        departure.booking_deadline = data["booking_deadline"]

    departure.save()
    return departure


def set_departure_status(departure_id, status):
    with transaction.atomic():
        departure = (
            Departure.objects.select_for_update()
            .select_related("tour")
            .filter(id=departure_id)
            .first()
        )
        if not departure:
            raise NotFound(f"Departure {departure_id} not found.")

        departure.status = status
        departure.save(update_fields=["status"])

        if status == DepartureStatus.COMPLETED:
            complete_bookings_for_departure(departure)

        return departure
