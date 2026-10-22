"""Serializers for the coupons application.
Formats coupon representations for administrative management and customer validation.
Validates promotional discount rules and expiry deadlines.
"""

from django.utils import timezone
from rest_framework import serializers

from apps.coupons.models import Coupon, CouponDiscountType


class CouponSerializer(serializers.ModelSerializer):
    discount_value = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=False
    )
    expires_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")

    class Meta:
        model = Coupon
        fields = [
            "id",
            "code",
            "discount_type",
            "discount_value",
            "expires_at",
            "max_uses",
            "times_used",
            "is_active",
        ]


class CouponValidateSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=30)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_subtotal(self, value):
        if value <= 0:
            raise serializers.ValidationError("Subtotal must be above 0.")
        return value


class CouponCreateSerializer(serializers.Serializer):
    code = serializers.CharField(min_length=3, max_length=30)
    discount_type = serializers.ChoiceField(choices=CouponDiscountType.choices)
    discount_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    expires_at = serializers.DateTimeField()
    max_uses = serializers.IntegerField(required=False, allow_null=True, min_value=1)

    def validate_code(self, value):
        val = value.strip().upper()
        if not val.isalnum():
            raise serializers.ValidationError("Code must contain only letters and digits.")
        if Coupon.objects.filter(code=val).exists():
            raise serializers.ValidationError("Coupon code already exists.")
        return val

    def validate_discount_value(self, value):
        if value <= 0:
            raise serializers.ValidationError("Must be above 0.")
        if (
            getattr(self, "initial_data", None)
            and self.initial_data.get("discount_type") == CouponDiscountType.PERCENT
            and value > 100
        ):
            raise serializers.ValidationError("Must be at most 100 for percent.")
        return value

    def validate_expires_at(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Expiry must be in the future.")
        return value

    def validate(self, attrs):
        if (
            attrs.get("discount_type") == CouponDiscountType.PERCENT
            and attrs.get("discount_value", 0) > 100
        ):
            raise serializers.ValidationError(
                {"discount_value": "Must be at most 100 for percent."}
            )
        return attrs


class CouponUpdateSerializer(serializers.Serializer):
    discount_type = serializers.ChoiceField(choices=CouponDiscountType.choices, required=False)
    discount_value = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    expires_at = serializers.DateTimeField(required=False)
    max_uses = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    is_active = serializers.BooleanField(required=False)

    def validate_discount_value(self, value):
        if value <= 0:
            raise serializers.ValidationError("Must be above 0.")
        if (
            getattr(self, "initial_data", None)
            and self.initial_data.get("discount_type") == CouponDiscountType.PERCENT
            and value > 100
        ):
            raise serializers.ValidationError("Must be at most 100 for percent.")
        return value

    def validate_expires_at(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Expiry must be in the future.")
        return value

    def validate(self, attrs):
        if (
            attrs.get("discount_type") == CouponDiscountType.PERCENT
            and attrs.get("discount_value", 0) > 100
        ):
            raise serializers.ValidationError(
                {"discount_value": "Must be at most 100 for percent."}
            )
        return attrs
