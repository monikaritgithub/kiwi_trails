"""Catalog domain services for tours categories and guides.
Provides query and retrieval functions for tourist activities.
Includes single query annotations to prevent N plus one queries.
"""

from django.db.models import (
    Avg,
    CharField,
    Count,
    DateTimeField,
    F,
    FloatField,
    IntegerField,
    OuterRef,
    Q,
    Subquery,
    Sum,
    Value,
)
from django.db.models.functions import Cast, Coalesce, Round
from django.utils import timezone

from apps.bookings.models import Booking, BookingStatus
from apps.catalog.models import Category, Guide, Tour, TourImage, TourStatus
from apps.core.exceptions import NotFound, ValidationFailed
from apps.departures.models import Departure, DepartureStatus
from apps.reviews.models import Review


def list_tours(filters):
    now = timezone.now()
    booked_subquery = (
        Booking.objects.filter(
            departure=OuterRef("pk"),
            status__in=[
                BookingStatus.PENDING,
                BookingStatus.APPROVED,
                BookingStatus.COMPLETED,
            ],
        )
        .values("departure")
        .annotate(total=Sum("traveller_count"))
        .values("total")
    )
    open_deps = (
        Departure.objects.filter(
            tour=OuterRef("pk"),
            status=DepartureStatus.SCHEDULED,
            booking_deadline__gte=now,
            start_datetime__gte=now,
        )
        .annotate(
            calculated_seats_left=F("capacity")
            - Coalesce(Subquery(booked_subquery, output_field=IntegerField()), Value(0))
        )
        .filter(calculated_seats_left__gt=0)
        .order_by("start_datetime")
    )
    next_dep_subquery = Subquery(
        open_deps.values("start_datetime")[:1],
        output_field=DateTimeField(),
    )
    seats_left_subquery = Subquery(
        open_deps.values("calculated_seats_left")[:1],
        output_field=IntegerField(),
    )
    first_image_subquery = Subquery(
        TourImage.objects.filter(tour=OuterRef("pk"))
        .order_by("sort_order", "id")
        .values("image_url")[:1],
        output_field=CharField(),
    )
    avg_rating_subquery = Subquery(
        Review.objects.filter(tour=OuterRef("pk"))
        .values("tour")
        .annotate(val=Cast(Round(Avg("rating"), 1), FloatField()))
        .values("val")[:1],
        output_field=FloatField(),
    )
    rev_count_subquery = Subquery(
        Review.objects.filter(tour=OuterRef("pk"))
        .values("tour")
        .annotate(val=Count("id"))
        .values("val")[:1],
        output_field=IntegerField(),
    )

    qs = (
        Tour.objects.filter(status=TourStatus.ACTIVE)
        .select_related("category")
        .annotate(
            annotated_image_url=first_image_subquery,
            annotated_average_rating=avg_rating_subquery,
            annotated_review_count=Coalesce(rev_count_subquery, Value(0)),
            annotated_next_departure=next_dep_subquery,
            annotated_seats_left=seats_left_subquery,
        )
    )

    search = filters.get("search")
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

    location = filters.get("location")
    if location:
        qs = qs.filter(location__iexact=location)

    category_id = filters.get("category_id")
    if category_id:
        try:
            cat_id = int(category_id)
            qs = qs.filter(category_id=cat_id)
        except (ValueError, TypeError):
            raise ValidationFailed(
                "Invalid category ID.",
                {"category_id": "Category ID must be an integer."},
            )

    min_price = filters.get("min_price")
    if min_price is not None and min_price != "":
        try:
            qs = qs.filter(price_per_person__gte=float(min_price))
        except (ValueError, TypeError):
            raise ValidationFailed(
                "Invalid minimum price.",
                {"min_price": "Minimum price must be a valid number."},
            )

    max_price = filters.get("max_price")
    if max_price is not None and max_price != "":
        try:
            qs = qs.filter(price_per_person__lte=float(max_price))
        except (ValueError, TypeError):
            raise ValidationFailed(
                "Invalid maximum price.",
                {"max_price": "Maximum price must be a valid number."},
            )

    sort = filters.get("sort") or "newest"
    allowed_sorts = {
        "newest": ("-created_at", "-id"),
        "price_asc": ("price_per_person", "-id"),
        "price_desc": ("-price_per_person", "-id"),
    }
    if sort not in allowed_sorts:
        raise ValidationFailed(
            "Invalid sort parameter.",
            {"sort": "Invalid sort option."},
        )

    return qs.order_by(*allowed_sorts[sort])


def get_tour(tour_id, user=None):
    tour = (
        Tour.objects.filter(id=tour_id)
        .select_related("category", "guide")
        .prefetch_related("images", "faqs")
        .first()
    )
    if not tour:
        raise NotFound(f"Tour {tour_id} not found.")

    is_admin = False
    if user and getattr(user, "is_authenticated", False):
        if getattr(user, "role", "") == "admin":
            is_admin = True

    if tour.status == TourStatus.ARCHIVED and not is_admin:
        raise NotFound(f"Tour {tour_id} not found.")

    reviews_agg = tour.reviews.aggregate(
        avg_rating=Round(Avg("rating"), 1),
        count=Count("id"),
    )
    tour.average_rating = reviews_agg["avg_rating"]
    tour.review_count = reviews_agg["count"]

    tour.upcoming_departures = list(
        tour.departures.filter(
            status=DepartureStatus.SCHEDULED,
            start_datetime__gte=timezone.now(),
        ).order_by("start_datetime")
    )
    return tour


def list_categories():
    return Category.objects.all().order_by("name")


def get_guide(guide_id):
    guide = Guide.objects.filter(id=guide_id).first()
    if not guide:
        raise NotFound(f"Guide {guide_id} not found.")
    return guide
