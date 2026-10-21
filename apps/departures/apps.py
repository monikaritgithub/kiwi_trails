"""
Application configuration for the departures app.
Manages tour departure dates, seat counts, and calendars.
"""

from django.apps import AppConfig


class DeparturesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.departures"
