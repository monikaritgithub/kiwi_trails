"""Service layer for accounts and authentication workflows.
Handles user registration token creation authentication and profile updates.
Enforces business rules and raises core api errors.
"""

from rest_framework.authtoken.models import Token

from apps.accounts.models import User
from apps.core.authentication import make_token
from apps.core.exceptions import EmailTaken, Unauthenticated, ValidationFailed


def register_user(data):
    email = data["email"].strip().lower()
    if User.objects.filter(email=email).exists():
        raise EmailTaken(
            "Email is already used.",
            {"email": "Email is already used."},
        )

    user = User.objects.create_user(
        email=email,
        full_name=data["full_name"].strip(),
        password=data["password"],
        phone=data.get("phone"),
    )
    return user


def login_user(email, password):
    clean_email = email.strip().lower()
    user = User.objects.filter(email=clean_email).first()
    if user is None or not user.check_password(password) or not user.is_active:
        raise Unauthenticated("Email or password is wrong.")

    token, expires_at = make_token(user)
    return token, expires_at, user


def logout_user(user):
    Token.objects.filter(user=user).delete()


def update_profile(user, data):
    if "current_password" in data and "new_password" in data:
        current_password = data["current_password"]
        new_password = data["new_password"]
        if not user.check_password(current_password):
            raise ValidationFailed(
                "Current password is wrong.",
                {"current_password": "Current password is wrong."},
            )
        user.set_password(new_password)

    if "full_name" in data:
        user.full_name = data["full_name"].strip()

    if "phone" in data:
        user.phone = data["phone"]

    user.save()
    return user
