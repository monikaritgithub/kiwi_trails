"""
Application configuration for the seeds app.
Provides management commands to seed demo data.
"""

from django.apps import AppConfig


class SeedsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.seeds"
