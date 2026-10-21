"""
Application configuration for the reviews app.
Manages tour reviews, ratings, and moderation.
"""

from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reviews"
