"""Coupon models for discounts and promotional campaigns.
Defines percentage and fixed discount vouchers with usage limits.
Used during price quotation and booking checkout.
"""

from django.db import models


class CouponDiscountType(models.TextChoices):
    PERCENT = "percent", "percent"
    FIXED = "fixed", "fixed"


class Coupon(models.Model):
    code = models.CharField(max_length=30, unique=True)
    discount_type = models.CharField(
        max_length=20,
        choices=CouponDiscountType.choices,
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    expires_at = models.DateTimeField()
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    times_used = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "coupons"

    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code
