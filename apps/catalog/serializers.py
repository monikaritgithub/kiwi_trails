"""Serializers for the catalog app.
Formats public representations of tours categories guides images and faqs.
Follows the Kiwi Trails tour and category shapes.
"""

from django.utils import timezone
from rest_framework import serializers

from apps.catalog.models import Category, Guide, Tour, TourFaq, TourImage
from apps.departures.models import Departure, DepartureStatus
from apps.departures.services import get_seats_taken, is_booking_open


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class GuideSerializer(serializers.ModelSerializer):
    languages = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Guide
        fields = ["id", "full_name", "bio", "photo_url", "languages"]

    def get_languages(self, obj):
        if not obj.languages:
            return []
        return [lang.strip() for lang in obj.languages.split(",") if lang.strip()]

    def get_bio(self, obj):
        return obj.bio or None

    def get_photo_url(self, obj):
        return obj.photo_url or None


class TourImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourImage
        fields = ["id", "image_url", "alt_text", "sort_order"]


class TourFaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourFaq
        fields = ["id", "question", "answer", "sort_order"]


class TourDepartureSerializer(serializers.ModelSerializer):
    tour_id = serializers.IntegerField(source="tour.id", read_only=True)
    start_datetime = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    booking_deadline = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    seats_taken = serializers.SerializerMethodField()
    seats_left = serializers.SerializerMethodField()
    booking_open = serializers.SerializerMethodField()

    class Meta:
        model = Departure
        fields = [
            "id",
            "tour_id",
            "start_datetime",
            "booking_deadline",
            "capacity",
            "seats_taken",
            "seats_left",
            "booking_open",
            "status",
        ]

    def get_seats_taken(self, obj):
        return get_seats_taken(obj)

    def get_seats_left(self, obj):
        taken = self.get_seats_taken(obj)
        return max(0, obj.capacity - taken)

    def get_booking_open(self, obj):
        return is_booking_open(obj)


class TourSummarySerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(source="category.id", read_only=True)
    category = serializers.CharField(source="category.name", read_only=True)
    price_per_person = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=False
    )
    image_url = serializers.CharField(source="annotated_image_url", default=None, allow_null=True)
    average_rating = serializers.FloatField(
        source="annotated_average_rating", default=None, allow_null=True
    )
    review_count = serializers.IntegerField(source="annotated_review_count", default=0)
    next_departure = serializers.DateTimeField(
        source="annotated_next_departure",
        default=None,
        allow_null=True,
        format="%Y-%m-%dT%H:%M:%SZ",
    )
    seats_left = serializers.IntegerField(
        source="annotated_seats_left", default=None, allow_null=True
    )

    class Meta:
        model = Tour
        fields = [
            "id",
            "title",
            "location",
            "category_id",
            "category",
            "price_per_person",
            "duration_days",
            "image_url",
            "average_rating",
            "review_count",
            "next_departure",
            "seats_left",
            "status",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data.get("image_url"):
            data["image_url"] = None
        return data


class TourDetailSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(source="category.id", read_only=True)
    category = serializers.CharField(source="category.name", read_only=True)
    price_per_person = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=False
    )
    accessibility_info = serializers.SerializerMethodField()
    visitor_guidelines = serializers.SerializerMethodField()
    meeting_point = serializers.SerializerMethodField()
    images = TourImageSerializer(many=True, read_only=True)
    guide = GuideSerializer(read_only=True)
    faqs = TourFaqSerializer(many=True, read_only=True)
    average_rating = serializers.FloatField(read_only=True, default=None, allow_null=True)
    review_count = serializers.IntegerField(read_only=True, default=0)
    departures = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = [
            "id",
            "title",
            "description",
            "location",
            "category_id",
            "category",
            "price_per_person",
            "duration_days",
            "itinerary",
            "accessibility_info",
            "visitor_guidelines",
            "meeting_point",
            "cancellation_days",
            "status",
            "images",
            "guide",
            "faqs",
            "average_rating",
            "review_count",
            "departures",
        ]

    def get_accessibility_info(self, obj):
        return obj.accessibility_info or None

    def get_visitor_guidelines(self, obj):
        return obj.visitor_guidelines or None

    def get_meeting_point(self, obj):
        if not obj.meeting_point_name:
            return None
        return {
            "name": obj.meeting_point_name,
            "lat": float(obj.meeting_lat) if obj.meeting_lat is not None else None,
            "lng": float(obj.meeting_lng) if obj.meeting_lng is not None else None,
        }

    def get_departures(self, obj):
        deps = getattr(obj, "upcoming_departures", None)
        if deps is None:
            deps = obj.departures.filter(
                status=DepartureStatus.SCHEDULED,
                start_datetime__gte=timezone.now(),
            ).order_by("start_datetime")
        return TourDepartureSerializer(deps, many=True).data
