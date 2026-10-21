"""Catalog domain services for tours categories and guides.
Provides query and retrieval functions for tourist activities.
Includes single query annotations to prevent N plus one queries.
"""

from django.core.files.storage import default_storage
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
from apps.catalog.models import (
    Category,
    Guide,
    Tour,
    TourFaq,
    TourImage,
    TourStatus,
)
from apps.core.exceptions import NotFound, ValidationFailed
from apps.departures.models import Departure, DepartureStatus
from apps.reviews.models import Review


def _annotate_tour_queryset(qs):
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

    return qs.select_related("category").annotate(
        annotated_image_url=first_image_subquery,
        annotated_average_rating=avg_rating_subquery,
        annotated_review_count=Coalesce(rev_count_subquery, Value(0)),
        annotated_next_departure=next_dep_subquery,
        annotated_seats_left=seats_left_subquery,
    )


def list_tours(filters):
    qs = _annotate_tour_queryset(Tour.objects.filter(status=TourStatus.ACTIVE))

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


def list_admin_tours(filters):
    status = filters.get("status")
    if status and status not in [TourStatus.ACTIVE, TourStatus.ARCHIVED]:
        raise ValidationFailed(
            "Invalid status parameter.",
            {"status": "Status must be active or archived."},
        )

    qs = Tour.objects.all()
    if status:
        qs = qs.filter(status=status)

    search = filters.get("search")
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

    qs = _annotate_tour_queryset(qs)
    return qs.order_by("-created_at", "-id")


def create_tour(data, user=None):
    tour = Tour.objects.create(
        title=data["title"],
        description=data["description"],
        location=data["location"],
        category_id=data["category_id"],
        price_per_person=data["price_per_person"],
        duration_days=data["duration_days"],
        itinerary=data["itinerary"],
        accessibility_info=data.get("accessibility_info") or "",
        visitor_guidelines=data.get("visitor_guidelines") or "",
        meeting_point_name=data.get("meeting_point_name") or "",
        meeting_lat=data.get("meeting_lat"),
        meeting_lng=data.get("meeting_lng"),
        guide_id=data.get("guide_id"),
        cancellation_days=data.get("cancellation_days", 7),
        status=TourStatus.ACTIVE,
    )
    return get_tour(tour.id, user=user)


def update_tour(tour_id, data, user=None):
    tour = Tour.objects.filter(id=tour_id).first()
    if not tour:
        raise NotFound(f"Tour {tour_id} not found.")

    for field, val in data.items():
        if val is None and field in [
            "accessibility_info",
            "visitor_guidelines",
            "meeting_point_name",
        ]:
            val = ""
        setattr(tour, field, val)

    tour.save()
    return get_tour(tour.id, user=user)


def set_tour_status(tour_id, status):
    tour = Tour.objects.filter(id=tour_id).first()
    if not tour:
        raise NotFound(f"Tour {tour_id} not found.")

    tour.status = status
    tour.save(update_fields=["status", "updated_at"])
    return {"id": tour.id, "status": tour.status}


def add_tour_image(tour_id, image_file, alt_text="", sort_order=0):
    tour = Tour.objects.filter(id=tour_id).first()
    if not tour:
        raise NotFound(f"Tour {tour_id} not found.")

    saved_path = default_storage.save(f"tours/{image_file.name}", image_file)
    saved_path = saved_path.replace("\\", "/")
    image_url = f"/media/{saved_path}"
    return TourImage.objects.create(
        tour=tour,
        image_url=image_url,
        alt_text=alt_text or "",
        sort_order=sort_order or 0,
    )


def delete_tour_image(image_id):
    tour_image = TourImage.objects.filter(id=image_id).first()
    if not tour_image:
        raise NotFound(f"Tour image {image_id} not found.")

    if tour_image.image_url.startswith("/media/"):
        rel_path = tour_image.image_url[len("/media/") :]
        if default_storage.exists(rel_path):
            default_storage.delete(rel_path)

    tour_image.delete()
    return {"deleted": True}


def create_faq(tour_id, data):
    tour = Tour.objects.filter(id=tour_id).first()
    if not tour:
        raise NotFound(f"Tour {tour_id} not found.")

    return TourFaq.objects.create(
        tour=tour,
        question=data["question"],
        answer=data["answer"],
        sort_order=data.get("sort_order", 0),
    )


def update_faq(faq_id, data):
    faq = TourFaq.objects.filter(id=faq_id).first()
    if not faq:
        raise NotFound(f"FAQ {faq_id} not found.")

    for k, v in data.items():
        setattr(faq, k, v)
    faq.save()
    return faq


def delete_faq(faq_id):
    faq = TourFaq.objects.filter(id=faq_id).first()
    if not faq:
        raise NotFound(f"FAQ {faq_id} not found.")

    faq.delete()
    return {"deleted": True}


def create_guide(data):
    langs = data.get("languages", [])
    lang_str = ", ".join(langs) if langs else ""
    return Guide.objects.create(
        full_name=data["full_name"],
        bio=data.get("bio") or "",
        photo_url=data.get("photo_url") or None,
        languages=lang_str,
    )


def update_guide(guide_id, data):
    guide = Guide.objects.filter(id=guide_id).first()
    if not guide:
        raise NotFound(f"Guide {guide_id} not found.")

    data_copy = dict(data)
    if "languages" in data_copy:
        langs = data_copy.pop("languages")
        guide.languages = ", ".join(langs) if langs else ""

    for k, v in data_copy.items():
        setattr(guide, k, v)

    guide.save()
    return guide


def create_category(name):
    return Category.objects.create(name=name.strip())


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
