"""Serializers for customer and administrative review representations.
Transforms review records into public and administrative response formats.
Validates review submissions including ratings and booking references.
"""

from rest_framework import serializers

from apps.reviews.models import Review
from apps.reviews.services import format_reviewer_name


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")

    class Meta:
        model = Review
        fields = [
            "id",
            "tour_id",
            "booking_id",
            "rating",
            "comment",
            "reviewer_name",
            "created_at",
        ]

    def get_reviewer_name(self, obj):
        return format_reviewer_name(obj.user)


class ReviewAdminSerializer(serializers.ModelSerializer):
    tour_title = serializers.CharField(source="tour.title", read_only=True)
    reviewer_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")

    class Meta:
        model = Review
        fields = [
            "id",
            "tour_id",
            "tour_title",
            "booking_id",
            "user_id",
            "rating",
            "comment",
            "reviewer_name",
            "created_at",
        ]

    def get_reviewer_name(self, obj):
        return format_reviewer_name(obj.user)


class ReviewCreateSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField(min_value=1)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
        default="",
    )
