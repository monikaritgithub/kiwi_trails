"""
Application configuration for the bookings app.
Manages tour reservations, status tracking, and attendance.
"""

from django.apps import AppConfig


class BookingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.bookings"
