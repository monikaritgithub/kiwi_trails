"""
Authentication classes and token utilities for Kiwi Trails.
Implements token expiration and Bearer token parsing.
"""

from datetime import timedelta

from django.utils import timezone
from rest_framework.authentication import TokenAuthentication

from apps.core.exceptions import Unauthenticated


class ExpiringTokenAuthentication(TokenAuthentication):
    keyword = "Bearer"

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related("user").get(key=key)
        except model.DoesNotExist:
            raise Unauthenticated("Invalid authentication token.")

        if not token.user.is_active:
            raise Unauthenticated("User account is disabled.")

        if timezone.now() - token.created > timedelta(hours=24):
            token.delete()
            raise Unauthenticated("Authentication token has expired.")

        return (token.user, token)


def make_token(user):
    from rest_framework.authtoken.models import Token

    Token.objects.filter(user=user).delete()
    token = Token.objects.create(user=user)
    expires_at = token.created + timedelta(hours=24)
    return (token, expires_at)
