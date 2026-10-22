"""Coupon service helpers for discounts and promotional vouchers.
Applies coupon codes to calculate discounts and marks coupons as used.
Provides query and management functions for administrative coupon operations.
"""

from decimal import ROUND_HALF_UP, Decimal

from django.db.models import F
from django.utils import timezone

from apps.core.exceptions import CouponInvalid, NotFound, ValidationFailed
from apps.coupons.models import Coupon, CouponDiscountType


def apply_coupon(code, subtotal):
    if not code or not isinstance(code, str):
        raise CouponInvalid(
            "This coupon does not exist.",
            {"code": "This coupon does not exist."},
        )

    clean_code = code.strip().upper()
    coupon = Coupon.objects.filter(code=clean_code).first()
    if not coupon:
        raise CouponInvalid(
            "This coupon does not exist.",
            {"code": "This coupon does not exist."},
        )

    if not coupon.is_active:
        raise CouponInvalid(
            "This coupon is not active.",
            {"code": "This coupon is not active."},
        )

    if coupon.expires_at < timezone.now():
        raise CouponInvalid(
            "This coupon has expired.",
            {"code": "This coupon has expired."},
        )

    if coupon.max_uses is not None and coupon.times_used >= coupon.max_uses:
        raise CouponInvalid(
            "This coupon has reached its maximum uses.",
            {"code": "This coupon has reached its maximum uses."},
        )

    subtotal_dec = Decimal(str(subtotal))
    if coupon.discount_type == CouponDiscountType.PERCENT:
        discount_amount = (subtotal_dec * coupon.discount_value) / Decimal("100")
    else:
        discount_amount = min(subtotal_dec, coupon.discount_value)

    discount_amount = discount_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    new_total = max(Decimal("0.00"), subtotal_dec - discount_amount)
    new_total = new_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return coupon, discount_amount, new_total


def mark_coupon_used(coupon):
    Coupon.objects.filter(id=coupon.id).update(times_used=F("times_used") + 1)
    coupon.refresh_from_db()


def list_coupons():
    return Coupon.objects.all().order_by("-id")


def create_coupon(data):
    code = data["code"].strip().upper()
    if Coupon.objects.filter(code=code).exists():
        raise ValidationFailed(
            "Coupon code already exists.",
            {"code": "Coupon code already exists."},
        )

    return Coupon.objects.create(
        code=code,
        discount_type=data["discount_type"],
        discount_value=data["discount_value"],
        expires_at=data["expires_at"],
        max_uses=data.get("max_uses"),
        is_active=True,
        times_used=0,
    )


def update_coupon(coupon_id, data):
    coupon = Coupon.objects.filter(id=coupon_id).first()
    if not coupon:
        raise NotFound(f"Coupon {coupon_id} not found.")

    dtype = data.get("discount_type", coupon.discount_type)
    dval = data.get("discount_value", coupon.discount_value)
    if dtype == CouponDiscountType.PERCENT and dval > 100:
        raise ValidationFailed(
            "Percent discount cannot exceed 100.",
            {"discount_value": "Must be at most 100 for percent."},
        )

    for key, val in data.items():
        if key != "code":
            setattr(coupon, key, val)

    coupon.save()
    return coupon
