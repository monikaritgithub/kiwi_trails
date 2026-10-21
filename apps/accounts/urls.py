"""URL routes for authentication and user accounts.
Maps endpoint paths to corresponding accounts views without trailing slashes.
Provides named patterns for api registration and profile operations.
"""

from django.urls import path

from apps.accounts.views import LoginView, LogoutView, MeView, RegisterView

urlpatterns = [
    path("auth/register", RegisterView.as_view(), name="auth-register"),
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("auth/logout", LogoutView.as_view(), name="auth-logout"),
    path("users/me", MeView.as_view(), name="users-me"),
]
