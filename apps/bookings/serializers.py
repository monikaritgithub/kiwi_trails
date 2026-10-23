"""Serializers for booking API requests.
Validates departure, traveller count, and optional coupon input.
"""

from rest_framework import serializers


class BookingQuoteSerializer(serializers.Serializer):
    departure_id = serializers.IntegerField(min_value=1)
    traveller_count = serializers.IntegerField(min_value=1)
    coupon_code = serializers.CharField(
        max_length=30,
        required=False,
        allow_blank=True,
        allow_null=True,
        default=None,
        trim_whitespace=True,
    )

    def validate_coupon_code(self, value):
        if not value:
            return None
        return value.upper()
