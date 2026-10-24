"""Views for booking API endpoints.
Handles customer quotes, booking creation, history, and booking details.
"""

from django.http import HttpResponse
from django.utils.http import content_disposition_header
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bookings.documents import (
    build_booking_calendar,
    build_booking_invoice,
)
from apps.bookings.models import BookingStatus
from apps.bookings.serializers import (
    BookingCancelSerializer,
    BookingCreateSerializer,
    BookingQuoteSerializer,
    BookingSerializer,
)
from apps.bookings.services import (
    calculate_booking_quote,
    cancel_booking,
    create_booking,
    get_booking_by_id,
    list_customer_bookings,
)
from apps.core.exceptions import Forbidden
from apps.core.pagination import ApiPagination
from apps.core.permissions import IsCustomer, IsOwnerOrAdmin
from apps.departures.models import DepartureStatus


class BookingQuoteView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request):
        serializer = BookingQuoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quote = calculate_booking_quote(**serializer.validated_data)
        return Response(quote)


class BookingCreateView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = create_booking(
            user=request.user,
            **serializer.validated_data,
        )

        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_201_CREATED,
        )


class BookingMyListView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request):
        bookings = list_customer_bookings(
            user=request.user,
            status=request.query_params.get("status"),
        )

        paginator = ApiPagination()
        page = paginator.paginate_queryset(bookings, request, view=self)
        serializer = BookingSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)


class BookingDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get(self, request, booking_id):
        booking = get_booking_by_id(booking_id)
        self.check_object_permissions(request, booking)

        return Response(BookingSerializer(booking).data)


class BookingCancelView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request, booking_id):
        booking = get_booking_by_id(booking_id)

        if booking.user_id != request.user.pk:
            raise Forbidden("You can only cancel your own bookings.")

        serializer = BookingCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = cancel_booking(
            user=request.user,
            booking_id=booking_id,
            **serializer.validated_data,
        )

        return Response(BookingSerializer(booking).data)


class BookingInvoiceView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get(self, request, booking_id):
        booking = get_booking_by_id(booking_id)
        self.check_object_permissions(request, booking)

        if booking.status not in [
            BookingStatus.APPROVED,
            BookingStatus.COMPLETED,
        ]:
            raise Forbidden("Invoices are available only for approved or completed bookings.")

        pdf_bytes = build_booking_invoice(booking)
        filename = f"invoice-{booking.booking_reference}.pdf"

        response = HttpResponse(
            pdf_bytes,
            content_type="application/pdf",
        )
        response["Content-Disposition"] = content_disposition_header(
            as_attachment=True,
            filename=filename,
        )
        response["Cache-Control"] = "private, no-store"
        return response


class BookingCalendarView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request, booking_id):
        booking = get_booking_by_id(booking_id)

        if booking.user_id != request.user.pk:
            raise Forbidden("You can only download calendars for your own bookings.")

        if booking.status not in [
            BookingStatus.PENDING,
            BookingStatus.APPROVED,
        ]:
            raise Forbidden(
                "Calendar downloads are available only for pending or approved bookings."
            )

        if booking.departure.status != DepartureStatus.SCHEDULED:
            raise Forbidden("Calendar downloads are available only for scheduled departures.")

        calendar_bytes = build_booking_calendar(booking)
        filename = f"{booking.booking_reference}.ics"

        response = HttpResponse(
            calendar_bytes,
            content_type="text/calendar; charset=utf-8",
        )
        response["Content-Disposition"] = content_disposition_header(
            as_attachment=True,
            filename=filename,
        )
        response["Cache-Control"] = "private, no-store"
        return response
