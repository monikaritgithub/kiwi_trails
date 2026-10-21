"""Serializers for the accounts application.
Validates registration login and user profile update requests.
Formats user data responses while excluding sensitive passwords.
"""

from rest_framework import serializers

from apps.accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "full_name", "email", "phone", "role", "created_at")
        read_only_fields = ("id", "full_name", "email", "phone", "role", "created_at")


class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(min_length=2, max_length=100)
    email = serializers.EmailField(max_length=150)
    password = serializers.CharField(min_length=8, write_only=True)
    phone = serializers.CharField(
        max_length=30,
        required=False,
        allow_null=True,
        allow_blank=True,
    )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserUpdateSerializer(serializers.Serializer):
    full_name = serializers.CharField(
        min_length=2,
        max_length=100,
        required=False,
    )
    phone = serializers.CharField(
        max_length=30,
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    current_password = serializers.CharField(
        required=False,
        write_only=True,
    )
    new_password = serializers.CharField(
        min_length=8,
        required=False,
        write_only=True,
    )

    def validate(self, attrs):
        has_curr = "current_password" in attrs
        has_new = "new_password" in attrs
        if has_curr != has_new:
            raise serializers.ValidationError(
                {"current_password": "Both current_password and new_password are required."}
            )
        return attrs
