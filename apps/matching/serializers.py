"""Serializers for trip match requests and results."""

from rest_framework import serializers


class MatchRequestSerializer(serializers.Serializer):
    interests = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list,
    )
    budget_per_person = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        min_value=0,
    )
    max_days = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )
    travellers = serializers.IntegerField(
        required=False,
        default=1,
        min_value=1,
    )
    accessibility_needs = serializers.BooleanField(
        required=False,
        default=False,
    )
    month = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=7,
    )
    prefer_maori_led = serializers.BooleanField(
        required=False,
        default=False,
    )

    def validate_month(self, value):
        if not value:
            return None
        parts = value.strip().split("-")
        if len(parts) != 2 or len(parts[0]) != 4 or len(parts[1]) != 2:
            raise serializers.ValidationError("Month must be in YYYY-MM format.")
        try:
            year = int(parts[0])
            month = int(parts[1])
            if year < 2000 or year > 2100 or month < 1 or month > 12:
                raise ValueError()
        except ValueError:
            raise serializers.ValidationError("Month must be a valid YYYY-MM date.")
        return value.strip()


class MatchResultItemSerializer(serializers.Serializer):
    tour_id = serializers.IntegerField()
    title = serializers.CharField()
    score = serializers.IntegerField()
    price_per_person = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=False
    )
    next_departure = serializers.CharField(allow_null=True)
    seats_left = serializers.IntegerField(allow_null=True)
    reasons = serializers.ListField(child=serializers.CharField())
    operator_name = serializers.CharField(allow_blank=True)
    maori_led = serializers.BooleanField()
    image_url = serializers.CharField(allow_null=True)
    location = serializers.CharField()
    category = serializers.CharField()
    duration_days = serializers.IntegerField()
