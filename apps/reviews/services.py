"""Review service helpers for customer feedback and administrative listings.
Formats reviewer display names and validates tour review eligibility.
Queries and filters reviews for public catalogs and admin moderation.
"""

from apps.bookings.services import get_completed_booking_for_user
from apps.catalog.models import Tour, TourStatus
from apps.core.exceptions import NotFound, ReviewNotAllowed, ValidationFailed
from apps.reviews.models import Review


def format_reviewer_name(user):
    full_name = getattr(user, "full_name", "") or ""
    parts = full_name.strip().split()
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0]} {parts[-1][0].upper()}."


def list_tour_reviews(tour_id, user=None):
    tour = Tour.objects.filter(id=tour_id).first()
    if not tour:
        raise NotFound(f"Tour {tour_id} not found.")

    is_admin = False
    if user and getattr(user, "is_authenticated", False):
        if getattr(user, "role", "") == "admin":
            is_admin = True

    if tour.status == TourStatus.ARCHIVED and not is_admin:
        raise NotFound(f"Tour {tour_id} not found.")

    return tour.reviews.select_related("user").order_by("-created_at", "-id")


def create_review(user, booking_id, rating, comment=""):
    booking = get_completed_booking_for_user(booking_id, user)
    if not booking:
        raise ReviewNotAllowed("Booking is not eligible for review.")

    if Review.objects.filter(booking=booking).exists():
        raise ReviewNotAllowed("This booking has already been reviewed.")

    tour = getattr(getattr(booking, "departure", None), "tour", None)
    if not tour:
        raise ReviewNotAllowed("Booking departure tour not found.")

    return Review.objects.create(
        booking=booking,
        user=user,
        tour=tour,
        rating=rating,
        comment=comment or "",
    )


def list_admin_reviews(filters=None):
    filters = filters or {}
    qs = Review.objects.select_related("tour", "user").order_by("-created_at", "-id")

    tour_id = filters.get("tour_id")
    if tour_id is not None and str(tour_id).strip() != "":
        try:
            tid = int(tour_id)
            qs = qs.filter(tour_id=tid)
        except (ValueError, TypeError):
            raise ValidationFailed(
                "Invalid tour ID.",
                {"tour_id": "Tour ID must be an integer."},
            )

    rating = filters.get("rating")
    if rating is not None and str(rating).strip() != "":
        try:
            r = int(rating)
            if r < 1 or r > 5:
                raise ValueError()
            qs = qs.filter(rating=r)
        except (ValueError, TypeError):
            raise ValidationFailed(
                "Invalid rating filter.",
                {"rating": "Rating must be an integer between 1 and 5."},
            )

    return qs
