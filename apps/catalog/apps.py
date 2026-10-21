"""
Application configuration for the catalog app.
Manages tours, categories, guides, images, and FAQs.
"""

from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalog"
