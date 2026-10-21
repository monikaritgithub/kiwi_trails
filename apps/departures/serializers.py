"""Serializers for the departures application.
Formats public representations of scheduled departures and calendar items.
Validates administrative departure creation and updates.
"""

from django.utils import timezone
from rest_framework import serializers

from apps.departures.models import Departure
from apps.departures.services import get_seats_taken, is_booking_open


class DepartureSerializer(serializers.ModelSerializer):
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


class DepartureCalendarItemSerializer(DepartureSerializer):
    tour_title = serializers.CharField(source="tour.title", read_only=True)

    class Meta:
        model = Departure
        fields = [
            "id",
            "tour_id",
            "tour_title",
            "start_datetime",
            "booking_deadline",
            "capacity",
            "seats_taken",
            "seats_left",
            "booking_open",
            "status",
        ]


class DepartureCreateSerializer(serializers.Serializer):
    start_datetime = serializers.DateTimeField()
    capacity = serializers.IntegerField()
    booking_deadline = serializers.DateTimeField()

    def validate_capacity(self, value):
        if value < 1:
            raise serializers.ValidationError("Capacity must be at least 1.")
        return value

    def validate_start_datetime(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Start datetime must be in the future.")
        return value

    def validate(self, attrs):
        start = attrs.get("start_datetime")
        deadline = attrs.get("booking_deadline")
        if start and deadline and deadline >= start:
            raise serializers.ValidationError(
                {"booking_deadline": "Booking deadline must be before start datetime."}
            )
        return attrs


class DepartureUpdateSerializer(serializers.Serializer):
    start_datetime = serializers.DateTimeField(required=False)
    capacity = serializers.IntegerField(required=False)
    booking_deadline = serializers.DateTimeField(required=False)

    def validate_capacity(self, value):
        if value < 1:
            raise serializers.ValidationError("Capacity must be at least 1.")
        return value

    def validate_start_datetime(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Start datetime must be in the future.")
        return value

    def validate(self, attrs):
        start = attrs.get("start_datetime")
        deadline = attrs.get("booking_deadline")
        if start and deadline and deadline >= start:
            raise serializers.ValidationError(
                {"booking_deadline": "Booking deadline must be before start datetime."}
            )
        return attrs


class DepartureStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["completed", "cancelled"])
