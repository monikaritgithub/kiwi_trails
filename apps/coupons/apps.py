"""
Application configuration for the coupons app.
Manages discount codes, usage limits, and validation.
"""

from django.apps import AppConfig


class CouponsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.coupons"
