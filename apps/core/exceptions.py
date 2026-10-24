"""
Exceptions and API exception handler for the core app.
Converts application errors and DRF exceptions into consistent JSON error responses.
"""

from django.http import Http404
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


class ApiError(Exception):
    code = "ERROR"
    status_code = 400

    def __init__(self, message, fields=None):
        super().__init__(message)
        self.message = message
        self.fields = fields or {}


class Unauthenticated(ApiError):
    code = "UNAUTHENTICATED"
    status_code = 401


class Forbidden(ApiError):
    code = "FORBIDDEN"
    status_code = 403


class NotFound(ApiError):
    code = "NOT_FOUND"
    status_code = 404


class ValidationFailed(ApiError):
    code = "VALIDATION_ERROR"
    status_code = 422


class EmailTaken(ApiError):
    code = "EMAIL_TAKEN"
    status_code = 409


class SeatsUnavailable(ApiError):
    code = "SEATS_UNAVAILABLE"
    status_code = 409


class BookingClosed(ApiError):
    code = "BOOKING_CLOSED"
    status_code = 409


class CancellationNotAllowed(ApiError):
    code = "CANCELLATION_NOT_ALLOWED"
    status_code = 409


class InvalidStatusChange(ApiError):
    code = "INVALID_STATUS_CHANGE"
    status_code = 409


class CapacityConflict(ApiError):
    code = "CAPACITY_CONFLICT"
    status_code = 409


class CouponInvalid(ApiError):
    code = "COUPON_INVALID"
    status_code = 422


class ReviewNotAllowed(ApiError):
    code = "REVIEW_NOT_ALLOWED"
    status_code = 403


def api_exception_handler(exc, context):
    if isinstance(exc, ApiError):
        return Response(
            {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "fields": exc.fields,
                },
            },
            status=exc.status_code,
        )

    if isinstance(exc, (serializers.ValidationError, exceptions.ValidationError)):
        fields = {}
        message = "Validation failed."
        if isinstance(exc.detail, dict):
            for field, errs in exc.detail.items():
                if isinstance(errs, list) and errs:
                    fields[field] = str(errs[0])
                elif isinstance(errs, str):
                    fields[field] = errs
                else:
                    fields[field] = str(errs)
        elif isinstance(exc.detail, list) and exc.detail:
            message = str(exc.detail[0])
        else:
            message = str(exc.detail)
        return Response(
            {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": message,
                    "fields": fields,
                },
            },
            status=422,
        )

    if isinstance(exc, (exceptions.NotAuthenticated, exceptions.AuthenticationFailed)):
        return Response(
            {
                "success": False,
                "error": {
                    "code": "UNAUTHENTICATED",
                    "message": str(exc.detail)
                    if hasattr(exc, "detail")
                    else "Authentication required.",
                    "fields": {},
                },
            },
            status=401,
        )

    if isinstance(exc, exceptions.PermissionDenied):
        return Response(
            {
                "success": False,
                "error": {
                    "code": "FORBIDDEN",
                    "message": str(exc.detail) if hasattr(exc, "detail") else "Permission denied.",
                    "fields": {},
                },
            },
            status=403,
        )

    if isinstance(exc, (exceptions.NotFound, Http404)):
        return Response(
            {
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": str(exc.detail) if hasattr(exc, "detail") else "Item not found.",
                    "fields": {},
                },
            },
            status=404,
        )

    response = drf_exception_handler(exc, context)
    if response is not None:
        return Response(
            {
                "success": False,
                "error": {
                    "code": "ERROR",
                    "message": str(response.data),
                    "fields": {},
                },
            },
            status=response.status_code,
        )

    return None
