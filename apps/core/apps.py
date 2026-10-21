"""
Application configuration for the core app.
Registers shared exceptions, renderers, permissions, and helpers.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
