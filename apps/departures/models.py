"""Departure models for tourist activities.
Defines scheduled departures start dates capacities and status tracking.
Used across booking and calendar views.
"""

from django.db import models


class DepartureStatus(models.TextChoices):
    SCHEDULED = "scheduled", "scheduled"
    COMPLETED = "completed", "completed"
    CANCELLED = "cancelled", "cancelled"


class Departure(models.Model):
    tour = models.ForeignKey(
        "catalog.Tour",
        on_delete=models.PROTECT,
        related_name="departures",
    )
    start_datetime = models.DateTimeField(db_index=True)
    capacity = models.PositiveIntegerField()
    booking_deadline = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=DepartureStatus.choices,
        default=DepartureStatus.SCHEDULED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "departures"
        indexes = [
            models.Index(fields=["start_datetime"]),
        ]

    def __str__(self):
        return f"{self.tour.title} at {self.start_datetime}"
