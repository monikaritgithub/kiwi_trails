"""
Test helpers for Kiwi Trails.
Provides factory functions to create users and authenticated API clients.
"""

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.core.authentication import make_token


def make_admin(email="admin@kiwitrails.test", full_name="Admin User", password="Password123!"):
    user_model = get_user_model()
    user, created = user_model.objects.get_or_create(
        email=email.lower(),
        defaults={"full_name": full_name, "role": "admin"},
    )
    if created or password:
        user.set_password(password)
        user.role = "admin"
        user.save()
    return user


def make_customer(
    email="customer@kiwitrails.test", full_name="Customer User", password="Password123!"
):
    user_model = get_user_model()
    user, created = user_model.objects.get_or_create(
        email=email.lower(),
        defaults={"full_name": full_name, "role": "customer"},
    )
    if created or password:
        user.set_password(password)
        user.role = "customer"
        user.save()
    return user


def make_client(user):
    client = APIClient()
    token, _ = make_token(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.key}")
    return client
