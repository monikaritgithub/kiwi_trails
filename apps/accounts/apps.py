"""
Application configuration for the accounts app.
Manages user accounts, authentication, and profiles.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
