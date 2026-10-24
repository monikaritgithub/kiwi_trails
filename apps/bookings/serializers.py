"""Serializers for booking API requests.
Validates quote input and optional traveller requirements.
"""

from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from apps.bookings.models import Booking, BookingStatus


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


class BookingCreateSerializer(BookingQuoteSerializer):
    pickup_preference = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        allow_null=True,
        default=None,
    )
    dietary_requirements = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        allow_null=True,
        default=None,
    )
    accessibility_needs = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        allow_null=True,
        default=None,
    )


class BookingSerializer(serializers.ModelSerializer):
    price_per_person = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=False
    )
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    discount_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=False
    )
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    coupon_code = serializers.CharField(source="coupon.code", read_only=True, allow_null=True)
    tour = serializers.SerializerMethodField()
    departure = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    cancel_deadline = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "id",
            "booking_reference",
            "status",
            "traveller_count",
            "price_per_person",
            "subtotal",
            "discount_amount",
            "total_price",
            "coupon_code",
            "pickup_preference",
            "dietary_requirements",
            "accessibility_needs",
            "status_reason",
            "cancelled_at",
            "can_cancel",
            "cancel_deadline",
            "tour",
            "departure",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_tour(self, booking):
        tour = booking.departure.tour
        return {
            "id": tour.id,
            "title": tour.title,
            "location": tour.location,
        }

    def get_departure(self, booking):
        departure = booking.departure
        return {
            "id": departure.id,
            "start_datetime": serializers.DateTimeField().to_representation(
                departure.start_datetime
            ),
        }

    def get_can_cancel(self, booking):
        deadline = booking.departure.start_datetime - timedelta(
            days=booking.departure.tour.cancellation_days
        )
        return (
            booking.status in [BookingStatus.PENDING, BookingStatus.APPROVED]
            and timezone.now() < deadline
        )

    def get_cancel_deadline(self, booking):
        deadline = booking.departure.start_datetime - timedelta(
            days=booking.departure.tour.cancellation_days
        )
        return serializers.DateTimeField().to_representation(deadline)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in [
            "pickup_preference",
            "dietary_requirements",
            "accessibility_needs",
            "status_reason",
        ]:
            data[field] = data[field] or None
        return data


class BookingCancelSerializer(serializers.Serializer):
    reason = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        allow_null=True,
        default=None,
        trim_whitespace=True,
    )


class AdminBookingFilterSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=BookingStatus.choices,
        required=False,
    )
    tour_id = serializers.IntegerField(min_value=1, required=False)
    departure_id = serializers.IntegerField(min_value=1, required=False)
    date_from = serializers.DateField(
        required=False,
        input_formats=["%Y-%m-%d"],
    )
    date_to = serializers.DateField(
        required=False,
        input_formats=["%Y-%m-%d"],
    )
    search = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )

    def validate(self, attrs):
        date_from = attrs.get("date_from")
        date_to = attrs.get("date_to")

        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError(
                {"date_to": "End date must be on or after start date."}
            )

        return attrs


class AdminBookingCustomerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    phone = serializers.CharField(read_only=True, allow_null=True)


class AdminBookingSerializer(BookingSerializer):
    customer = AdminBookingCustomerSerializer(source="user", read_only=True)
    attendance = serializers.SerializerMethodField()

    class Meta(BookingSerializer.Meta):
        fields = BookingSerializer.Meta.fields + [
            "customer",
            "attendance",
        ]
        read_only_fields = fields

    def get_attendance(self, booking):
        attendance = getattr(booking, "attendance", None)
        return attendance.status if attendance is not None else None


class AdminBookingStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            BookingStatus.APPROVED,
            BookingStatus.REJECTED,
            BookingStatus.CANCELLED,
            BookingStatus.COMPLETED,
        ],
        required=True,
    )
    reason = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        allow_null=True,
        default=None,
        trim_whitespace=True,
    )


class BookingAttendanceSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(source="id", read_only=True)
    customer_name = serializers.CharField(
        source="user.full_name",
        read_only=True,
    )
    attendance = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "booking_id",
            "booking_reference",
            "customer_name",
            "traveller_count",
            "attendance",
        ]
        read_only_fields = fields

    def get_attendance(self, booking):
        attendance = getattr(booking, "attendance", None)
        return attendance.status if attendance is not None else None
