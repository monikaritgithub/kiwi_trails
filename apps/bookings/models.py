"""Booking and attendance models for reservations.
Stores customer bookings passenger counts pricing references and attendance.
Follows the Kiwi Trails booking domain specification.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models


class BookingStatus(models.TextChoices):
    PENDING = "pending", "pending"
    APPROVED = "approved", "approved"
    REJECTED = "rejected", "rejected"
    CANCELLED = "cancelled", "cancelled"
    COMPLETED = "completed", "completed"


class AttendanceStatus(models.TextChoices):
    PRESENT = "present", "present"
    ABSENT = "absent", "absent"


class Booking(models.Model):
    booking_reference = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="bookings",
    )
    departure = models.ForeignKey(
        "departures.Departure",
        on_delete=models.PROTECT,
        related_name="bookings",
    )
    traveller_count = models.PositiveIntegerField()
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    coupon = models.ForeignKey(
        "coupons.Coupon",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="bookings",
    )
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
    )
    pickup_preference = models.CharField(max_length=255, blank=True)
    dietary_requirements = models.CharField(max_length=255, blank=True)
    accessibility_needs = models.CharField(max_length=255, blank=True)
    status_reason = models.CharField(max_length=255, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bookings"
        indexes = [
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.booking_reference


class Attendance(models.Model):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="attendance",
    )
    status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
    )
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="attendances_marked",
    )
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendance"

    def __str__(self):
        return f"{self.booking.booking_reference}: {self.status}"
